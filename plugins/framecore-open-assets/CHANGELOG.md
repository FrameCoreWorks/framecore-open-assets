# Changelog

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
