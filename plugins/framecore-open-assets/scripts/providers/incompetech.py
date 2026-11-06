import re
import urllib.parse

from core import asset, variant, MAX_FILE

CATALOG = 'https://incompetech.com/music/royalty-free/pieces.json'
MP3 = 'https://incompetech.com/music/royalty-free/mp3-royaltyfree/'
PAGE = 'https://incompetech.com/music/royalty-free/index.html?isrc='
CC_BY_4 = 'https://creativecommons.org/licenses/by/4.0/'
# Observed 2026-11-06: catalogue MP3s are about 320 kbit/s (40 kB/s); a 58:54 track is 141 MB.
BYTES_PER_SECOND = 40_100


def seconds(length):
    try:
        h, m, s = (int(x) for x in str(length).split(':'))
        return h * 3600 + m * 60 + s
    except ValueError:
        return 0


def search(client, query, category, limit):
    data = client.json(CATALOG, 'Read the public Incompetech catalogue (title, feel, BPM, instruments, MP3 file)')
    terms = [t for t in re.findall(r'\w+', str(query).lower()) if t]
    scored = []
    for i, piece in enumerate(data if isinstance(data, list) else []):
        name, isrc, length = piece.get('filename'), piece.get('isrc'), seconds(piece.get('length'))
        if not name or not isrc or not length or length * BYTES_PER_SECOND > MAX_FILE:
            continue
        text = ' '.join(str(piece.get(k) or '') for k in ('title', 'feel', 'description', 'instruments')).lower()
        score = sum(t in text for t in terms)
        if terms and not score:
            continue
        scored.append((-score, i, piece, length))
    out = []
    for _, _, piece, length in sorted(scored)[:limit]:
        title = piece.get('title') or piece['filename'].rsplit('.', 1)[0]
        url = MP3 + urllib.parse.quote(piece['filename'])
        facts = {k: piece[k] for k in ('bpm', 'feel', 'instruments') if piece.get(k)}
        out.append(asset('incompetech', piece['isrc'], title, 'Kevin MacLeod (incompetech.com)',
                         PAGE + urllib.parse.quote(piece['isrc']),
                         [variant(url, 'MP3', duration_seconds=length, **facts)], CC_BY_4, category,
                         ['Credit required: "' + title + ' Kevin MacLeod (incompetech.com) Licensed under '
                          'Creative Commons: By Attribution 4.0 https://creativecommons.org/licenses/by/4.0/".',
                          'The CC BY 4.0 licence is stated site-wide (FAQ), not on each file; keep the source page.',
                          'Platform Content ID claims by third parties can still occur; the credit and licence are '
                          'the dispute evidence.']))
    return out
