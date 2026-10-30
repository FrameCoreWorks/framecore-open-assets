from core import asset, variant, endpoint, PDM


SFX_FILTER = ' deepcat:"Sound effects"'
UNFILED = ('This audio is not filed under Commons Sound effects; it may be speech or music. '
           'Listen before using it as a sound effect.')


def query_commons(client, search, limit):
    return client.json(endpoint('https://commons.wikimedia.org/w/api.php', action='query', format='json',
                                generator='search', gsrsearch=search,
                                gsrnamespace=6, gsrlimit=limit, prop='imageinfo',
                                iiprop='url|extmetadata|mime', iiurlwidth=800, maxlag=5),
                       'Search Commons file records with creator and file-specific licence metadata')


def search(client, query, category, limit):
    kind = 'audio' if category in ('audio', 'music', 'sfx') else 'video' if category == 'video' else 'bitmap'
    notes = []
    if category == 'sfx':
        data = query_commons(client, query + ' filetype:audio' + SFX_FILTER, limit)
        if not data.get('query', {}).get('pages'):
            data = query_commons(client, query + ' filetype:audio', limit)
            notes = [UNFILED]
    else:
        data = query_commons(client, query + ' filetype:' + kind, limit)
    out = []
    for page in data.get('query', {}).get('pages', {}).values():
        for info in page.get('imageinfo', [])[:1]:
            meta = info.get('extmetadata', {})
            field = lambda key: meta.get(key, {}).get('value', '')
            licence = field('LicenseUrl')
            if not licence and field('LicenseShortName') == 'Public domain' and field('Copyrighted') == 'False':
                licence = PDM
            links = []
            if kind == 'bitmap' and info.get('thumburl'):
                links.append(variant(info['thumburl'], 'thumbnail'))
            if info.get('url'):
                links.append(variant(info['url'], 'original'))
            warnings = [field('Restrictions')] if field('Restrictions') else []
            out.append(asset('commons', page['pageid'], page['title'], field('Artist'),
                             info.get('descriptionurl'), links, licence, category, warnings + notes,
                             review='blocked' if warnings else None))
    return out
