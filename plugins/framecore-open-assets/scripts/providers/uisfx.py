"""UI SFX (romainsimon/uisfx): 78 semantic UI cues in 12 sound packs, CC0 audio, pinned commit.

The audio is procedurally generated and dedicated to the public domain (LICENSE-AUDIO at the pin). The taxonomy
page lists the cue names and their use; every cue exists in every pack at sounds/{pack}/{cue}.mp3.
"""
import re
import urllib.parse

from core import asset, variant, CC0

PIN = '9950fe66f993a6660dab9c2651dcbcd899ffd83b'
RAW = f'https://raw.githubusercontent.com/romainsimon/uisfx/{PIN}/'
PAGE = f'https://github.com/romainsimon/uisfx/tree/{PIN}'
PACKS = ('minimal', 'soft', 'glass', 'arcade', 'mechanical', 'organic', 'dreamy', 'scifi', 'rubber', 'cinematic',
         'studio', 'zen')
ROW = re.compile(r'^\|\s*`([a-z0-9-]+)`\s*\|\s*([^|]*)\|', re.M)


def search(client, query, category, limit):
    body, _ = client.get(RAW + 'docs/taxonomy.md', 'Read the UI SFX cue taxonomy (cue names and their use)', accept='*/*')
    cues = [(m[1], m[2].strip()) for m in ROW.finditer(body.decode('utf-8', 'replace'))]
    terms = {t for t in re.findall(r'\w+', str(query).lower()) if t}
    packs = [p for p in PACKS if p in terms]
    ordered = packs + [p for p in PACKS if p not in packs]
    ranked = []
    for cue, use in cues:
        text = set(re.findall(r'\w+', (cue.replace('-', ' ') + ' ' + use).lower()))
        hit = len(terms & text)
        if terms and not hit and not packs:
            continue
        ranked.append((-hit, cue, use))
    out = []
    for _, cue, use in sorted(ranked)[:limit]:
        variants = [variant(RAW + f'packages/uisfx/sounds/{p}/{urllib.parse.quote(cue)}.mp3', f'{p}/{cue}.mp3') for p in ordered]
        out.append(asset('uisfx', cue, 'UI cue: ' + cue.replace('-', ' '), 'UI SFX (romainsimon/uisfx)', PAGE, variants, CC0,
                         category, ['Use for: ' + use, 'Procedurally generated audio, not recordings; the repository is new '
                                    '(created July 2026), so pin to the reviewed commit.']))
    return out
