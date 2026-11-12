"""Fontsource: 2,100 open fonts (Google Fonts and others) with licence data, served from a pinned CDN version.

Only OFL-1.1, Apache-2.0, MIT and CC0 fonts are listed (Ubuntu Font Licence and others are skipped). Fontsource
splits fonts by script: Polish text needs BOTH the `latin` file (A-Z, ó) and the `latin-ext` file (ą ę ł ń ś ź ż),
so a Polish query returns both. File URLs come from the font's API record and carry the exact npm version.
"""
import re

from core import asset, variant, license_policy

API = 'https://api.fontsource.org/v1/fonts'
POLISH = {'polish', 'polski', 'polskie', 'latin-ext', 'latinext', 'diacritics', 'ogonki'}
WEIGHTS = ('400', '700')
FORMATS = ('ttf', 'woff2')


def search(client, query, category, limit):
    limit = min(limit, 4)
    terms = {t for t in re.findall(r'[\w-]+', str(query).lower()) if t}
    polish = bool(terms & POLISH)
    terms -= POLISH
    fonts = client.json(API, 'Read the Fontsource font list (family, category, subsets and licence per font)')
    ranked = []
    for i, f in enumerate(fonts if isinstance(fonts, list) else []):
        if license_policy(str(f.get('license', '')))[1] == 'blocked':
            continue
        if polish and 'latin-ext' not in f.get('subsets', []):
            continue
        text = set(re.findall(r'[\w-]+', ' '.join([f['id'], f.get('family', ''), f.get('category', '')]).lower()))
        hit = len(terms & text)
        if terms and not hit:
            continue
        ranked.append((-hit, i, f))
    out = []
    for _, _, f in sorted(ranked, key=lambda r: (r[0], r[1]))[:limit]:
        detail = client.json(f"{API}/{f['id']}", 'Read the font record: version and per-file CDN URLs')
        subsets = ['latin', 'latin-ext'] if polish else [detail.get('defSubset', 'latin')]
        variants = []
        for w in WEIGHTS:
            for sub in subsets:
                files = ((detail.get('variants', {}).get(w) or {}).get('normal') or {}).get(sub, {}).get('url', {})
                for fmt in FORMATS:
                    if files.get(fmt):
                        variants.append(variant(files[fmt], f"{f['id']} {w} {sub} {fmt}"))
        if not variants:
            continue
        lic_name, _ = license_policy(str(detail.get('license', '')))
        warnings = [f"Licence {lic_name} (font family \"{detail.get('family')}\", source {detail.get('source', 'see Fontsource')}). "
                    'Keep the font\'s copyright notice and licence with any font file you redistribute; text rendered '
                    'into a video or image is ordinary use.',
                    'Files are script subsets (' + ', '.join(subsets) + '). '
                    + ('Polish needs both the latin and latin-ext files.' if polish else
                       'Add "polish" to the query for the latin-ext files needed for ą ę ł ń ś ź ż.')]
        out.append(asset('fontsource', f['id'], detail.get('family') or f['id'],
                         detail.get('author') or f'{detail.get("family")} authors (see source)',
                         f"https://fontsource.org/fonts/{f['id']}", variants[:8],
                         detail.get('source') or 'https://fontsource.org/', category, warnings,
                         license_id=str(detail.get('license', ''))))
    return out
