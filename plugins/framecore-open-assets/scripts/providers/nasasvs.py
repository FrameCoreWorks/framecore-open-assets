"""NASA Scientific Visualization Studio (svs.gsfc.nasa.gov): visualizations, B-roll and stills.

SVS states that its content is in the public domain unless noted and that licensed music in some videos is
not. Rights stay behind the `review_nasa` gate, like the NASA Image and Video Library. File sizes appear only
as "[185.1 MB]" in the page description, so renditions over about 31 MiB are skipped and no byte count is
promised to the downloader.
"""
import re

from core import asset, variant, endpoint, https, MAX_FILE

API = 'https://svs.gsfc.nasa.gov/api/'
HELP = 'https://svs.gsfc.nasa.gov/help/'
UNITS = {'KB': 1024, 'MB': 1024 ** 2, 'GB': 1024 ** 3}
SIZE = re.compile(r'([^|\s][^|]*?)\s*\((?:\d+x\d+)\)\s*\[([\d.]+)\s*(KB|MB|GB)\]')
MEDIA = {'photos': 'Image', 'video': 'Movie'}
SCAN = 5


def sizes(description):
    return {m[1].strip(): float(m[2]) * UNITS[m[3]] for m in SIZE.finditer(description or '')}


def search(client, query, category, limit):
    wanted = MEDIA[category]
    data = client.json(endpoint(API + 'search/', search=query, limit=SCAN),
                       'Search SVS pages; the result list has no files, so each page is read next')
    out = []
    for row in data.get('results', []):
        if len(out) >= limit:
            break
        if row.get('result_type') == 'Hyperwall':
            continue
        page = client.json(API + str(row['id']) + '/', 'Read the page media list and the sizes in its description')
        known = sizes(page.get('description'))
        variants = []
        for group in page.get('media_groups', []):
            for entry in group.get('items', []):
                inst = entry.get('instance') or {}
                size = known.get(inst.get('filename'))
                if (inst.get('media_type') != wanted or not inst.get('url') or not size or size > MAX_FILE * 0.97
                        or inst.get('filename', '').endswith(('_thm.png', '_searchweb.png'))):
                    continue
                variants.append(variant(inst['url'], f"{inst['filename']} ({inst.get('width')}x{inst.get('height')}, "
                                        f"about {size / 1024 ** 2:.1f} MB)"))
        if not variants:
            continue
        credits = [p['name'] for c in page.get('credits', [])[:1] for p in c.get('people', [])[:3]]
        source = https(page.get('url') or f"https://svs.gsfc.nasa.gov/{row['id']}/")
        item = asset('nasasvs', row['id'], page.get('title'), '; '.join(credits) or 'NASA/GSFC Scientific Visualization Studio',
                     source, variants[:8], HELP, category,
                     ['SVS content is public domain unless noted; licensed music in some videos is not. Use videos '
                      'without their audio track unless the page says otherwise.',
                      'Credit "NASA\'s Scientific Visualization Studio"; no NASA endorsement may be implied.'],
                     review='review_nasa')
        item['license'] = 'NASA media (public domain unless noted on the page)'
        item['attribution'] = (f"{item['title']} — {item['creator']}, NASA's Scientific Visualization Studio. "
                               f"{source}. {item['license']}: {HELP}")
        out.append(item)
    return out
