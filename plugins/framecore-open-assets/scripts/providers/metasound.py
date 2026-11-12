"""Meta Open Sound, Oculus Audio Pack 1 (CC BY 4.0): 289 game and VR sound effects, pinned commit.

One request reads the pack manifest; the UCS file names (for example UIAlert_CasualMusicalError_OS_01.wav) carry
the category and description, so query words are matched against them. Playable files are the OGG previews in
the repository; the lossless WAVs are release attachments and are not used. CC BY 4.0 requires the fixed credit
from the pack's ATTRIBUTION.md.
"""
import re
import urllib.parse

from core import asset, variant

PIN = '251c0be57d5d1b3242b91f53e0cde62ab1cb42d9'
BASE = f'https://raw.githubusercontent.com/facebookincubator/Meta-open-sound/{PIN}/corpora/oculus-audio-pack/'
PAGE = f'https://github.com/facebookincubator/Meta-open-sound/tree/{PIN}/corpora/oculus-audio-pack'
CC_BY_4 = 'https://creativecommons.org/licenses/by/4.0/'
CREDIT = ('"Oculus Audio Pack 01" by Oculus VR, LLC (https://developers.meta.com/vr/downloads/package/oculus-audio-pack-1/), '
          'licensed under CC BY 4.0. Files renamed to the UCS naming convention; OGG previews transcoded from the original WAVs.')


def words(text):
    return {w.lower() for w in re.findall(r'[A-Z]+(?![a-z])|[A-Z]?[a-z]+|\d+', text)}


def search(client, query, category, limit):
    manifest = client.json(BASE + 'manifest.json', 'Read the pack manifest (UCS file names, durations)')
    terms = {t for t in re.findall(r'\w+', str(query).lower()) if t}
    sounds = {}
    for s in manifest.get('samples', []):
        name = s.get('file', '')
        if not name.endswith('.wav'):
            continue
        stem = name[:-4]
        sounds.setdefault(re.sub(r'_\d+$', '', stem), []).append((stem, s))
    ranked = []
    for key, takes in sounds.items():
        hit = len(terms & words(key))
        if terms and not hit:
            continue
        ranked.append((-hit, key, takes))
    out = []
    for _, key, takes in sorted(ranked)[:limit]:
        variants = [variant(BASE + 'ogg/' + urllib.parse.quote(stem) + '.ogg', stem + '.ogg',
                            duration_seconds=s.get('duration_s'), channels=s.get('channels')) for stem, s in sorted(takes)]
        out.append(asset('metasound', key, key.replace('_', ' '), 'Oculus VR, LLC', PAGE, variants[:6], CC_BY_4, category,
                         ['Credit required, exactly: ' + CREDIT,
                          'Only the OGG previews are used; lossless WAVs are GitHub Release attachments.']))
    return out
