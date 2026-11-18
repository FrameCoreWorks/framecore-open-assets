# Kenney audio packs (CC0, GitHub mirrors)

Sources: [Kenney asset pages](https://kenney.nl/assets/category:Audio) (licence CC0 1.0, read 2026-11-18 with a browser user agent; not used by the module) and the licence files in six GitHub mirrors, each pinned:

| Pack | Mirror | Commit | Sounds |
| --- | --- | --- | --- |
| UI Audio | [Calinou/kenney-ui-audio](https://github.com/Calinou/kenney-ui-audio) | `8c3d81b9159d058c444f89d12d518276b0b09345` | 51 |
| Interface Sounds | [Calinou/kenney-interface-sounds](https://github.com/Calinou/kenney-interface-sounds) | `4596a49eaf5a533948d49a47467f606bcdea70ff` | 100 |
| Impact Sounds | [Boyquotes/kenney-impact-sounds-for-godot](https://github.com/Boyquotes/kenney-impact-sounds-for-godot) | `999dd1684873f8b020a3aa5b26e713da21688924` | 130 |
| Sci-Fi Sounds | [Boyquotes/kenney-sci-fi-sounds-for-godot](https://github.com/Boyquotes/kenney-sci-fi-sounds-for-godot) | `c094967fe930c57ddb376f67c75f8aa0296690b7` | 73 |
| Digital Audio | [Boyquotes/kenney-digital-audio-for-godot](https://github.com/Boyquotes/kenney-digital-audio-for-godot) | `185a77e7c675341ad8d0805b3bbe4f20427c2481` | 62 |
| RPG Audio | [Boyquotes/kenney-rpg-audio-for-godot](https://github.com/Boyquotes/kenney-rpg-audio-for-godot) | `22eb79bb843bbcadcaa6ed119353a33265ffad11` | 51 |

467 short game sound effects by Kenney (impacts on metal, wood, glass, plate and soft surfaces, punches, footsteps on five surfaces, UI clicks, switches, rollovers, confirmations, errors, glitches, scroll and scratch, lasers, force fields, engines, explosions, power-ups, phasers, zaps, and RPG foley: books, cloth, doors, coins, knives). CC0 1.0: commercial use, no credit required; Kenney asks for an optional credit. The Calinou mirrors carry Kenney's original `License.txt`; the Boyquotes ports carry the CC0 1.0 legal code.

Why mirrors: kenney.nl disallows AI agents (ClaudeBot, Claude-User and others) in its robots.txt, and every crawler under `/assets/` and `/downloads/`, so the module never contacts kenney.nl. CC0 allows redistribution, so the GitHub copies carry the same rights. The mirrors are third-party ports (Calinou is a Godot maintainer; Boyquotes ports to the Godot Asset Library); byte equality with Kenney's current ZIPs was not checked (NOT_RUN), because that would need kenney.nl.

No account or key. The file names are embedded in the module (read from the pinned trees on 2026-11-18), so a search makes no request. Query words are matched against file names, with a small synonym map for reel vocabulary (hit, boom, glitch, typing, ui, hover, notification, riser, foley, page, coin, transition). Synonym-only matches for riser, transition, glitch and typing carry an "approximate match" warning. A download reads one WAV or OGG from raw.githubusercontent.com. Gaps: no real whooshes or long cinematic risers; the sounds are short (mostly under 2 s).

Live check 2026-11-18 (Claude Code cloud): "glitch" verified one WAV (0.02 s) and "impact metal" downloaded one OGG (0.17 s); both fully decoded, CC0, eligible. ChatGPT Work: NOT_RUN.
