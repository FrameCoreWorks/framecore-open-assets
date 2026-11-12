"""Iconify: 276 open icon, emoji, flag and logo sets (about 480,000 icons) behind one keyless API.

Every set declares its author and SPDX licence in the collections metadata returned with the search. Only sets
whose licence passes the runtime policy (CC0, CC BY, CC BY-SA, MIT, ISC, Apache-2.0, BSD, OFL) are listed;
GPL and non-commercial sets (for example gridicons, wordpress, dashicons, gala, icomoon-free, et, cbi, ps) are
dropped by that policy. Logo sets are CC0 or MIT as files, but the brands stay trademarks, so they keep a review
gate. The public API is a courtesy service with unspecified limits: one search plus one SVG per download.
"""
import urllib.parse

from core import asset, variant, endpoint, license_policy

API = 'https://api.iconify.design/'
# Remix Icon moved to a custom licence upstream in January 2026 while npm and Iconify still say Apache-2.0.
DENY = {'ri', 'remixicon'}
TRADEMARK_CATEGORIES = ('logos', 'brand')


def search(client, query, category, limit):
    limit = min(limit, 5)
    data = client.json(endpoint(API + 'search', query=query, limit=64),
                       'Search the Iconify index; the response carries each set\'s author and SPDX licence')
    sets = data.get('collections') or {}
    seen, first, rest = set(), [], []
    for name in data.get('icons', []):
        prefix, _, icon = name.partition(':')
        if not icon or prefix in DENY or prefix not in sets:
            continue
        (rest if prefix in seen else first).append((prefix, icon))
        seen.add(prefix)
    out = []
    for prefix, icon in first + rest:
        if len(out) >= limit:
            break
        meta = sets[prefix]
        lic = meta.get('license') or {}
        name, status = license_policy(lic.get('spdx') or lic.get('title') or '')
        author = (meta.get('author') or {}).get('name') or ''
        if status == 'blocked' or not author:
            continue
        logo = any(k in str(meta.get('category', '')).lower() for k in TRADEMARK_CATEGORIES)
        warnings = [f"Set \"{meta.get('name', prefix)}\" by {author}, licence {name} ({lic.get('url', 'no URL given')}). "
                    'Keep the author, licence and notice with the files you distribute.']
        if name.startswith('CC BY'):
            warnings.append('Credit the author as the licence requires.')
        if logo:
            warnings.append('Brand logo: the file licence does not cover the trademark; check the brand\'s usage rules '
                            'and never imply endorsement.')
        source = f"https://icon-sets.iconify.design/{prefix}/{icon}/"
        item = asset('iconify', f'{prefix}:{icon}', f"{meta.get('name', prefix)}: {icon}", author, source,
                     [variant(API + f"{urllib.parse.quote(prefix)}/{urllib.parse.quote(icon)}.svg", f'{icon}.svg')],
                     lic.get('url') or '', category, warnings, review='review_jurisdiction' if logo else None,
                     license_id=lic.get('spdx') or lic.get('title'))
        out.append(item)
    return out
