"""Adbertiser SFX (Reodelbasalan/adbertiser-sfx): 408 sound effects for reels and ads, CC0, pinned commit.

One request reads catalog.json (name, category, tags, description, duration). Query words are matched against those
fields; each record is one WAV. Every sound is synthesised from the repository's own generator code (no samples);
the repository is new (November 2026), so only the reviewed commit is read.
"""
import re
import urllib.parse

from core import asset, variant, CC0

PIN = 'ed6482ebd9c1283db4ee11b69dba3426c7dd5046'
BASE = f'https://raw.githubusercontent.com/Reodelbasalan/adbertiser-sfx/{PIN}/'
PAGE = f'https://github.com/Reodelbasalan/adbertiser-sfx/tree/{PIN}'


def words(text):
    return {w for w in re.split(r'[^a-z0-9]+', str(text).lower()) if w}


def search(client, query, category, limit):
    data = client.json(BASE + 'catalog.json', 'Read the Adbertiser SFX catalogue (names, tags, durations)')
    sounds = data if isinstance(data, list) else data.get('sounds', [])
    terms = words(query)
    ranked = []
    for s in sounds:
        name = words(s.get('name', '')) | words(s.get('category', ''))
        tags = set().union(set(), *(words(t) for t in s.get('tags', [])))
        hit = 3 * len(terms & name) + 2 * len(terms & tags) + len(terms & words(s.get('description', '')))
        hit += 4 * bool(terms & {re.split(r'[^a-z0-9]+', s.get('name', '').lower())[0]})
        if terms and not hit or not s.get('file'):
            continue
        ranked.append((-hit, s.get('name', ''), s))
    out = []
    for _, sid, s in sorted(ranked, key=lambda r: r[:2])[:limit]:
        notes = ['CC0 1.0: commercial use, no credit required.',
                 'Synthesised from code in the repository (no samples); new repository, pinned to the reviewed commit.']
        if s.get('description'):
            notes.append('Use for: ' + s['description'])
        out.append(asset('adbertiser', sid, sid.replace('_', ' '), 'Reodelbasalan (Adbertiser)', PAGE,
                         [variant(BASE + urllib.parse.quote(s['file']), s['file'].rsplit('/', 1)[-1],
                                  duration_seconds=s.get('duration'), channels=s.get('channels'))],
                         CC0, category, notes))
    return out
