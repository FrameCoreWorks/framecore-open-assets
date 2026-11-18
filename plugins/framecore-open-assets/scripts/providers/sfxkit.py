"""SFX Kit (wyzowl/sfx-kit): 320 sound effects for videos, animations and interfaces, CC0, pinned commit.

One request reads sounds.json (name, category, tags, use and avoid notes, duration, sync point, loudness). Query
words are matched against those fields; each record is one WAV. The sounds are synthesised by code (made with an AI
model, directed by Wyzowl, per the README); the licence is CC0 1.0.
"""
import re
import urllib.parse

from core import asset, variant, CC0

PIN = '92780e7ab0cdfb557497a988089c47f46e8c7412'
BASE = f'https://raw.githubusercontent.com/wyzowl/sfx-kit/{PIN}/'
PAGE = f'https://github.com/wyzowl/sfx-kit/tree/{PIN}'


def words(text):
    return {w for w in re.split(r'[^a-z0-9]+', str(text).lower()) if w}


def search(client, query, category, limit):
    data = client.json(BASE + 'sounds.json', 'Read the SFX Kit catalogue (names, tags, use, timing)')
    terms = words(query)
    ranked = []
    for s in data.get('sounds', []):
        name = words(s.get('id', '')) | words(s.get('name', '')) | words(s.get('category', ''))
        tags = set().union(*(words(t) for t in s.get('tags', []))) if s.get('tags') else set()
        text = words(s.get('description', '')) | set().union(set(), *(words(u) for u in s.get('use_for', [])))
        hit = 3 * len(terms & name) + 2 * len(terms & tags) + len(terms & text)
        hit += 4 * bool(terms & {re.split(r'[^a-z0-9]+', s.get('id', '').lower())[0]})
        if terms and not hit or not s.get('file'):
            continue
        ranked.append((-hit, s.get('id', ''), s))
    out = []
    for _, sid, s in sorted(ranked, key=lambda r: r[:2])[:limit]:
        sync = s.get('sync') or {}
        notes = ['CC0 1.0: commercial use, no credit required.',
                 'Synthesised by code (made with an AI model, directed by Wyzowl); not recordings.']
        if s.get('use_for'):
            notes.append('Use for: ' + '; '.join(s['use_for']))
        if s.get('avoid_for'):
            notes.append('Avoid for: ' + '; '.join(s['avoid_for']))
        if sync.get('at') is not None:
            notes.append(f"Sync point {sync['at']} s ({sync.get('meets', 'peak')}).")
        out.append(asset('sfxkit', sid, s.get('name', sid), 'Wyzowl', PAGE,
                         [variant(BASE + urllib.parse.quote(s['file']), s['file'].rsplit('/', 1)[-1],
                                  duration_seconds=s.get('duration'), channels=s.get('channels'))],
                         CC0, category, notes))
    return out
