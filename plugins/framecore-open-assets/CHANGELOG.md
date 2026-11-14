# Changelog

## 0.8.3, 2026-11-14

Trigger: the owner approved ("Tak", 2026-11-14) a fuller welcome text with no link to another plugin; 0.8.2 carried an earlier draft.

- `assets/startup-welcome.en.md` and the embedded copy in `SKILL.md` now hold the approved text: what Open Assets does, four kinds of material, the licence note (commercial-use sources, no accounts, credit and Content ID warnings), four numbered examples and a closing request.
- `welcome_test.py` checks bullets and numbered examples instead of bold bullets.
- Checks: `tools/check.py` passes. ChatGPT Work, Codex and Claude apps: NOT_RUN.

## 0.8.2, 2026-11-14

Trigger: owner request 2026-11-14 ("dodać stałe powitanie", then "Rozpisz lepiej każde powitanie. I nie dawaj odnośnika do głównej wtyczki"): a bare invocation got a two-line improvised answer that differed between hosts.

- A fixed English welcome, `skills/open-assets/assets/startup-welcome.en.md`: what Open Assets finds (photos and illustrations, textures and graphics, icons and fonts, music and sound effects, video), the licence record, four example requests and one closing question. No link to another plugin.
- `SKILL.md` embeds the same text in a new "Welcome" section with the rule: on a bare invocation output only the welcome, copied exactly in English or translated in full into the user's language, then wait.
- New `tests/welcome_test.py` checks that the embedded block is byte-identical to the asset and keeps its shape; `tools/check.py` runs it.
- Checks: `tools/check.py` passes. ChatGPT Work, Codex and Claude apps: NOT_RUN.

## 0.8.1, 2026-11-14

Trigger: the owner's end-to-end test of 2026-11-13: Kevin MacLeod's CC BY 4.0 "Pixelland" (Incompetech) was muted on Pinterest, while only the Incompetech and Internet Archive records warned about Content ID; Commons and National Jukebox music carried no warning.

- Every `music` record now carries one platform warning, added in `core.asset`: platforms detect music and can mute the film or file a claim even under a free licence; tell the user before it goes into a published film. The Incompetech and Internet Archive music records no longer carry their own Content ID line, so the warning appears once. The skill and the Incompetech dossier say so.
- Checks: `tools/check.py` passes; new regression test. Live searches: not repeated (no provider request changed). ChatGPT Work, Codex and Claude apps: NOT_RUN.

## 0.8.0, 2026-11-12

Trigger: owner decision 2026-11-12 ("Tak, dodaj Open Assets, Iconify i Font Source") on the two candidates the 0.7.0 research left for his decision.

- New categories `icons` and `fonts`. New providers `iconify` (icons from open-licensed sets) and `fontsource` (OFL, Apache and MIT web fonts, pinned CDN files, Polish needs `latin` and `latin-ext`). 22 providers, 36 provider/category paths.
- Licence policy: SPDX identifiers are now understood (MIT, ISC, Apache-2.0, BSD, OFL-1.1, CC0, CC BY, CC BY-SA); permissive and CC BY licences require a named creator. GPL, NC, the Ubuntu Font Licence, Remix Icon and sets without an author stay blocked. Logo sets are `review_jurisdiction` (trademark).
- Safety: new SVG decoder (static, self-contained SVG only) and font decoder (WOFF/WOFF2 header, FreeType load); `download` checks that icons are vector and fonts are fonts. The shared task contract is unchanged (`media_kind` is a free string).
- Allowlist: `api.iconify.design`, `api.fontsource.org`, `cdn.jsdelivr.net` (`docs/CLOUD_NETWORK.md`).
- Evidence: live search and download in a Claude Code cloud container; five new regression tests with trimmed live fixtures. ChatGPT Work: NOT_RUN.

## 0.7.0, 2026-11-12

Trigger: owner request 2026-11-12 to add the new sources from the "Nowe źródła dla Open Assets" research (about 270 sources checked; report in the project files) to the plugin and publish.

- New providers: `archive` (Internet Archive; whitelisted collections only; music, sfx, audio, video), `jukebox` (LoC National Jukebox, recordings before 1923, `review_jurisdiction`), `nasasvs` (NASA SVS stills and videos, `review_nasa`), `metasound` (Meta Open Sound, Oculus Audio Pack, CC BY 4.0 with the fixed credit) and `uisfx` (UI SFX, CC0). 20 providers, 34 provider/category paths.
- Licence safety: Internet Archive licence labels are declared by the uploader, so the module never searches the whole archive and re-checks the returned `licenseurl` against the policy. GitHub-hosted sources are pinned to reviewed commits.
- Allowlist: `svs.gsfc.nasa.gov` and `raw.githubusercontent.com` are new (`docs/CLOUD_NETWORK.md`); `archive.org` and the LoC hosts were already listed.
- Not included, by decision of the research: National Screening Room (MP4 copies mostly over the 32 MiB cap), Citizen DJ (audio on the shared `s3.amazonaws.com` host), Getty, Polona (POST search), National Gallery of Art (CSV only), ESO and ESA/Hubble (feed only), Iconify and Fontsource (need new categories and licence classes). They stay in the report for a separate owner decision.
- Evidence: live search, download and full decode in a Claude Code cloud container for each new provider (NASA SVS: a still; its videos rarely fit the cap). ChatGPT Work: NOT_RUN. Tests: five new regression tests with trimmed live fixtures.

## 0.6.0, 2026-11-11

- NASA audio: the existing NASA adapter searches `media_type=audio` (owner decision 2026-11-11, research DR-04), at most three records per search, smallest renditions first, duplicate manifest rows removed; `review_nasa` unchanged. 25 provider/category paths.
- Tests: fixture test for audio search, rendition order and review status (replaces the photos/video-only test). Live audio search and manifest read 2026-11-11; audio download/decode on a host NOT_RUN.

## 0.5.0, 2026-11-06

Trigger: owner request 2026-11-06 to add Pinterest (terryso/mcp-pinterest) to Open Assets as a source of references,
clearly separated from the free sources for commercial use; delivered as a pull request at the owner's request.

- New skill section 6 and `references/reference-sources.md`: Pinterest as a reference-only source (moodboard, style
  research, reference pack), used through the optional Toolbox connector `pinterest-references`. Kept pins go to
  `references/pinterest/` with a `.reference.json` (pin link, author or `Unknown`, query, date, "not cleared").
- No runtime change: Pinterest is not in `providers.json` and the runtime never calls it. Without the connector the
  skill says so and continues.
- Checks: `tools/check.py`. Host behaviour: NOT_RUN.

## 0.4.3, 2026-11-06

Trigger: the owner asked to add Incompetech after the 2026-11-06 Deep Research review of new free sources ("dołącz do Open Assets, jeśli pasuje na 100%"); music was the catalogue's largest gap (Commons only).

- New provider `incompetech` (music): Kevin MacLeod's catalogue under CC BY 4.0 through the public `pieces.json`
  and direct MP3 files, no account or key. Records carry BPM, feel and instruments on the variant, the site's
  required credit and a Content ID warning. Pieces over the 32 MiB cap (30 of 1,443, up to 141 MB) are skipped.
- Allowlist: `incompetech.com` (`docs/CLOUD_NETWORK.md`).
- Evidence: live search, download and full decode in a Claude Code cloud container (dossier). ChatGPT Work: NOT_RUN.
- Checks: `tools/check.py` passes; new regression test with an observed catalogue fixture.

## 0.4.2, 2026-11-04

Trigger: GPT Astra external audit 2026-11-04 (Open Assets 0.4.1 at `b15c35a`), each finding checked in the source.

- `contract.md` said every command accepts the envelope flags; only `status`, `search`, `verify` and `download` do
  (`domains` and `reach` are read-only helpers with no envelope). Audit ORCH-08.
- The Commons dossier still said only JPEG was tested; the 0.2.0 ChatGPT Work qualification covered all six
  packaged categories, and the dossier now says so. Audit ASSET-002 (the index was right).
- Repository: the README's "If search fails" explains that `reach` checks a connection only, not an HTTP answer
  (401, 403, 429, CAPTCHA or proxy refusals still happen), and asks before switching provider. Audit ASSET-001.
  CI pins Pillow 13.0.0 and its actions to full commits (`6eacf91`).
- Checks: `tools/check.py` passes. Host reruns: NOT_RUN.

## 0.4.1, 2026-10-31

Trigger: the 2026-10-31 Codex desktop retest of 0.3.1 (report U6, U12, U13).

- The native Codex entry quotes the runtime path in its `status --host codex` command, so a bundle under a
  folder such as `Codex&Claude` or with spaces no longer breaks in the shell (exit 127). `INSTALL.md` quotes
  the same command.
- Poly Haven records read `/info/{id}` and name the asset's authors as creator and its display name as title;
  the "Assets provided by Poly Haven" service credit stays.
- Commons sound-effect searches look in `deepcat:"Sound effects"` first. When that finds nothing, the plain
  audio search runs and each result carries a warning that it may be speech or music.



Trigger: in a Claude Code cloud thread Open Assets failed because the default network policy blocks the
provider hosts, and the runtime reported only a generic `transport_error`.

- New `reach` command: opens one connection to port 443 of each provider host (through the host's proxy
  when set), sends no HTTP request, and reports reachable/blocked providers, the blocked hosts, the full
  allowlist and workaround advice.
- New `domains` command: prints every reviewed provider host once, one per line, ready for a network allowlist.
- A proxy refusing the tunnel (403/407) now fails with `network_blocked` (envelope status `blocked`) and a
  `next_action` that says not to retry and offers the three workarounds.
- The skill runs `reach` before the first search and explains a block in one or two sentences.
  Repository guide: `docs/CLOUD_NETWORK.md`.

## 0.3.1, 2026-10-30

- `status` accepts an optional `--host` and then reports readiness only for that host; without it the output is
  unchanged. The installation guide's `status --host codex` step now works (it exited with code 2 in 0.3.0).
- Repository tool `tools/install_codex.py` (`plan`/`install`/`verify`, no network) installs one native
  `open-assets` entry in a Codex skill scope backed by the complete plugin bundle, like Creative Studio and Toolbox.
- The plugin README carries the one-step Claude Code install line.

## 0.3.0, 2026-10-29

- Optional `framecore-task-result/1` envelope (`--envelope-out`, `--task-id`, `--requester`, `--owner`) defined by
  the shared schema in `contracts/`, and a `capabilities.json` discovery manifest. Stdout and existing flags are unchanged.
- The `.asset.json` sidecar adds `host`, `model`, `runtime_version`, `fingerprint`, `search_utc`, `search_query`,
  `task_id`, `trace_sha256` and `hash_source`; existing fields are unchanged.
- A technical-only verification no longer unlocks a production `download`.
- Handoff text names Toolbox's built-in Earshot capability instead of a separate Earshot plugin path;
  repository URLs point to this repository; the contract lists every error code.

## 0.2.1, 2026-10-28

Only confirmed providers and media categories are distributed. The registry, provider dossiers and
CLI choices match the fourteen implemented providers; unused media handling is removed.
Per-asset rights checks, current-host verification and Studio/Earshot handoffs remain unchanged.

## 0.2.0, 2026-10-28

Four newly qualified image providers, host/category proof binding, provider pacing and media-type checks. Real Work validation and provenance handoff to Earshot/Studio.

## 0.1.1, 2026-10-28

- Align all three manifest licence declarations with the bundled Apache-2.0 licence.
- Guard the manifest agreement in the package regression test.
- Use OS-owned provider locks so completed or interrupted processes do not leave a permanent busy state; retain serial request pacing and reject real concurrency.

## 0.1.0, 2026-10-28

Owner-authorized creation of FrameCore Open Assets, using Earshot's Claude/ChatGPT/Codex packaging pattern.

- One sourcing skill, three consistent manifests, a portable Python CLI and ten separate provider adapters.
- Provider dossiers record official source URLs and reading dates.
- Per-asset rights gates, local host/category verification, signed search results, serial identified requests,
  HTTP cache controls, bounded downloads, full media decoding and provenance sidecars.
- No automatic source switching, paid generation, credentials, scraping or protection bypass.
- Source/package tests and actual Work CLI tests are distinct from fresh installed-client and Claude evidence.
