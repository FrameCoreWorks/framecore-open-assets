from core import asset, variant, endpoint

# Audio (owner decision 2026-11-11, research DR-04): at most three records per search, so one search plus three
# manifests stay within six metadata requests; the smallest renditions come first.
AUDIO_LIMIT = 3


def rank(url):
    for i, mark in enumerate(('~preview.', '~small.', '~64k.', '~128k.', '~mobile.', '~medium.')):
        if mark in url:
            return i
    return 9


def search(client, query, category, limit):
    kind = {'photos': 'image', 'video': 'video', 'audio': 'audio'}[category]
    if kind == 'audio':
        limit = min(limit, AUDIO_LIMIT)
    data = client.json(endpoint('https://images-api.nasa.gov/search', q=query, media_type=kind, page_size=limit),
                       'Search NASA Image and Video Library records and their media manifests')
    out = []
    for row in data.get('collection', {}).get('items', [])[:limit]:
        obj = row['data'][0]
        manifest = client.json(row['href'], 'Read the asset manifest and choose a real media rendition')
        extensions = {'image': ('.jpg', '.png'), 'video': ('.mp4',), 'audio': ('.mp3', '.m4a', '.wav')}[kind]
        urls = list(dict.fromkeys(u for u in manifest if isinstance(u, str) and u.lower().endswith(extensions)))
        urls.sort(key=lambda u: (rank(u), u))
        from urllib.parse import quote
        out.append(asset('nasa', obj['nasa_id'], obj.get('title'), obj.get('photographer') or obj.get('center'),
                         'https://images.nasa.gov/details/' + quote(obj['nasa_id'], safe=''),
                         [variant(u, u.rsplit('/', 1)[-1]) for u in urls],
                         'https://www.nasa.gov/nasa-brand-center/images-and-media/', category,
                         ['NASA is not a blanket CC0 source. Review third-party credits, people, logos and endorsement restrictions.',
                          obj.get('description', '')], review='review_nasa'))
    return out
