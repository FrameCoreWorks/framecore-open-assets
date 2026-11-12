"""Internet Archive: whitelisted collections only; licence from the item's own `licenseurl` field.

Licence labels on archive.org are declared by the uploader and are not checked by the Archive, so the
adapter never searches the whole site: every category is bound to reviewed collections or identifiers,
and the licence URL must still pass `license_policy` (CC0, PDM, CC BY, CC BY-SA).
"""
import urllib.parse

from core import asset, variant, endpoint, license_policy, MAX_FILE, clean

SEARCH = 'https://archive.org/advancedsearch.php'
META = 'https://archive.org/metadata/'
DOWNLOAD = 'https://archive.org/download/'
DETAILS = 'https://archive.org/details/'
LICENCES = ('http://creativecommons.org/publicdomain/zero/1.0/', 'http://creativecommons.org/publicdomain/mark/1.0/',
            'http://creativecommons.org/licenses/by/4.0/', 'http://creativecommons.org/licenses/by/3.0/',
            'http://creativecommons.org/licenses/by-sa/4.0/', 'http://creativecommons.org/licenses/by-sa/3.0/')
# Reviewed 2026-11-12 (research report "Nowe źródła dla Open Assets"). Add a collection only after reading it.
SCOPE = {
    'music': ('mediatype:audio AND (collection:(musopen OR netlabels) OR identifier:(OpenGoldbergVariations OR '
              '"The_Open_Goldberg_Variations-11823" OR "bach-well-tempered-clavier-book-1" OR '
              '"master-tracks-the-open-well-tempered-clavier"))', 'audio'),
    'sfx': ('mediatype:audio AND collection:radio-aporee-maps', 'audio'),
    'audio': ('mediatype:audio AND collection:radio-aporee-maps', 'audio'),
    'video': ('mediatype:movies AND identifier:(Sita_Sings_the_Blues OR BigBuckBunny_124 OR Sintel OR '
              'ElephantsDream)', 'video'),
}
AUDIO_FORMATS = ('VBR MP3', '128Kbps MP3', '64Kbps MP3', '256Kbps MP3', 'MP3', 'Ogg Vorbis')
VIDEO_FORMATS = ('h.264', 'MPEG4', '512Kb MPEG4', 'h.264 IA', 'h.264 HD')
MAX_VARIANTS = 8


def first(value):
    if isinstance(value, list):
        return '; '.join(clean(v) for v in value if clean(v))
    return clean(value)


def files_for(identifier, files, kind):
    wanted = AUDIO_FORMATS if kind == 'audio' else VIDEO_FORMATS
    chosen = []
    for f in files:
        if f.get('format') not in wanted or f.get('private') == 'true':
            continue
        size = int(f.get('size') or 0)
        if not size or size > MAX_FILE:
            continue
        chosen.append((wanted.index(f['format']), f['name'], size))
    best = {}
    for rank, name, size in sorted(chosen):
        stem = name.rsplit('.', 1)[0]
        best.setdefault(stem, (rank, name, size))
    rows = sorted(best.values(), key=lambda r: r[1])[:MAX_VARIANTS]
    return [variant(DOWNLOAD + urllib.parse.quote(identifier, safe='') + '/' + urllib.parse.quote(name, safe=''),
                    name, bytes=size) for _, name, size in rows]


def search(client, query, category, limit):
    scope, kind = SCOPE[category]
    terms = ' '.join(t for t in str(query).replace('"', ' ').split() if t)
    licence = ' OR '.join('"' + u + '"' for u in LICENCES)
    q = f'({scope}) AND licenseurl:({licence})' + (f' AND ({terms})' if terms else '')
    data = client.json(endpoint(SEARCH, q=q, rows=6, output='json', sort='downloads desc',
                                **{'fl[]': 'identifier'}),
                       'Search whitelisted Internet Archive collections for items with an open licence URL')
    out = []
    for doc in data.get('response', {}).get('docs', []):
        if len(out) >= limit:
            break
        ident = doc['identifier']
        meta = client.json(META + urllib.parse.quote(ident, safe=''),
                           'Read the item metadata (licence URL, creator) and its real file list')
        m = meta.get('metadata', {})
        licence_url = first(m.get('licenseurl'))
        if license_policy(licence_url)[1] == 'blocked':
            continue
        variants = files_for(ident, meta.get('files', []), kind)
        if not variants:
            continue
        warnings = ['The licence is declared by the uploader and is not verified by the Internet Archive; '
                    'keep the item page and licence URL as evidence.',
                    'Platform Content ID claims can still occur; the licence URL is the dispute evidence.']
        if category == 'video' and ident == 'Sita_Sings_the_Blues':
            warnings.append('Use the picture only: the Annette Hanshaw songs are licensed separately.')
        if category in ('sfx', 'audio'):
            warnings.append('Field recordings may contain voices, brands or private places; review before publishing.')
        out.append(asset('archive', ident, m.get('title'), first(m.get('creator')) or first(m.get('uploader')),
                         DETAILS + urllib.parse.quote(ident, safe=''), variants, licence_url, category, warnings))
    return out
