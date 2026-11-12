"""Library of Congress National Jukebox: acoustic recordings published before 1923.

The collection's rights statement says recordings published before 1923 are in the US public domain (Music
Modernization Act). That covers the recording in the United States only: the musical composition, other
jurisdictions, privacy and offensive period content still need a human review, so every asset keeps the
`review_jurisdiction` gate and needs a written review note before download.
"""
import re

from core import asset, variant, endpoint, https

COLLECTION = 'https://www.loc.gov/collections/national-jukebox/'
RIGHTS = COLLECTION + 'about-this-collection/rights-and-access/'
SCAN = 8


def search(client, query, category, limit):
    data = client.json(endpoint(COLLECTION, fo='json', q=query, c=SCAN),
                       'Search the National Jukebox; only recordings dated 1922 or earlier qualify')
    out = []
    for row in data.get('results', []):
        if len(out) >= limit:
            break
        m = re.match(r'(\d{4})', str(row.get('date') or ''))
        if (not m or int(m[1]) > 1922 or row.get('access_restricted') or not row.get('id')
                or 'sound recording' not in ' '.join(row.get('original_format', [])).lower()):
            continue
        urls = [r['media'] for r in row.get('resources', []) if str(r.get('media', '')).endswith('.mp3')]
        if not urls:
            continue
        page = https(row['id'])
        item = asset('jukebox', page.rstrip('/').rsplit('/', 1)[-1], row.get('title'),
                     '; '.join(row.get('contributor', [])[:3]) or 'Library of Congress', page,
                     [variant(urls[0], 'MP3 recording')], RIGHTS, category,
                     ['Recording published before 1923: public domain in the United States (LoC statement). The musical '
                      'composition, performers\' rights outside the US, privacy and offensive period content still need review.',
                      'Credit line requested by the Library: Library of Congress, National Jukebox.'],
                     review='review_jurisdiction')
        item['license'] = 'Public domain in the US (Library of Congress rights statement)'
        item['attribution'] = (f"{item['title']} — {item['creator']}. Library of Congress, National Jukebox. "
                               f"{page}. {item['license']}: {RIGHTS}")
        out.append(item)
    return out
