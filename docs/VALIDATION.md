# Validation

## 0.7.0 source (2026-11-12)

Five new providers from the 2026-11-12 research: `archive`, `jukebox`, `nasasvs`, `metasound`, `uisfx`. Live in a Claude Code
cloud container (host `claude_code`, open network): each category was searched; `verify` downloaded and fully decoded one
file per provider (archive: music MP3 3.3 MB, sfx MP3 4.1 MB, video MP4 10.9 MB; jukebox: MP3 3 min; metasound: OGG 1.2 s;
uisfx: MP3 0.6 s; nasasvs: JPEG 1024x576). NASA SVS photos search returned records; no SVS video within the 32 MiB cap was found for the queries
tried, and the National Screening Room (films are mostly over the cap) was left out. Hosted ChatGPT Work update, Work
search/download, Codex and Claude apps: NOT_RUN. `python3 tools/check.py`: see the commit.

## 0.6.0 source (2026-11-11)

NASA audio added to the existing adapter. `python3 tools/check.py` and `python3 tools/package.py`: see the commit. Live: one audio search and two manifests read on 2026-11-11 (no download). Audio download/decode on a host, ChatGPT Work, Claude and Codex installs: NOT_RUN.

## 0.5.0 source (2026-11-06)

Documentation and skill text only: Pinterest as a reference-only source through the optional Toolbox connector; no
runtime or provider change. `python3 tools/check.py`: see the commit. Connector use from Open Assets, hosted ChatGPT
Work update, Codex and Claude apps: NOT_RUN.

## 0.4.3 source (2026-11-06)

New Incompetech music provider. Live in a Claude Code cloud container (host `claude_code`, default network
policy): `search --provider incompetech --category music --query "calm piano"` returned three eligible CC BY 4.0
records; `verify` downloaded "Grand Dark Waltz Trio Vivace" (3,449,364 bytes) and decoded it fully (172.4 s MP3).
`python3 tools/check.py`: see the commit. Hosted ChatGPT Work update and Work search/download, Codex and Claude
apps: NOT_RUN.

## 0.4.2 source (2026-11-04)

Documentation fixes from the GPT Astra audit (see `plugins/framecore-open-assets/CHANGELOG.md`); no runtime code
changed. `python3 tools/check.py` passes in a Claude Code cloud container (Python 3.13, Pillow 13.0.0). Hosted
ChatGPT Work update, Codex and Claude apps: NOT_RUN.

## 0.4.1 source (2026-10-31)

Execution environment: Claude Code cloud container, Linux, provider hosts blocked. New offline tests (quoted
Codex status command with `&` and a space, Poly Haven author credit from a fixture shaped by the published
OpenAPI schema, Commons sound-effect filter and fallback) failed on 0.4.0 and pass on 0.4.1. Live Poly Haven
`/info` and Commons `deepcat` responses, Codex, Claude apps and the hosted ChatGPT Work update: NOT_RUN.

## 0.4.0 source (2026-10-30)

Execution environment: Claude Code cloud container, Linux, default network policy. Before (0.3.1 code path): a proxy refusal of a Commons search surfaced as
`transport_error` (`Tunnel connection failed: 403 Forbidden`). After: `runtime.py reach` reported
`network: blocked`, no ready providers and 32 refused hosts; the same search failed with `network_blocked` and the
workaround `next_action`. `python3 tools/check.py`: PASS (runtime 20, providers 7, package 4, contract 17, network 7, Codex installer 4 tests; reproducible ZIP; extracted runtime status); `network_test.py` uses a local fake proxy and makes
no provider calls. Behaviour after an allowlist change, Codex, Claude apps and the hosted ChatGPT Work update: NOT_RUN.

## 0.3.1 source (2026-10-30)

Fixes from the 2026-10-30 fresh-install test of Studio, Toolbox and Open Assets. Execution environment: Claude Code on macOS, Python 3.9.6 for `tools/check.py`, Python 3.13 for the extracted runtime. `python3 tools/check.py`: PASS (runtime 20, providers 7, package 4, contract 17, Codex installer 4 tests; reproducible ZIP; extracted runtime status). Smoke test: `tools/install_codex.py install` then `verify` into fresh absolute paths: FILES_VERIFIED, 65 files; `runtime.py status --host codex` from the bundle: 0.3.1, host results for `codex` only; `verify` still passes after the runtime wrote `__pycache__`. Codex session activation, hosted ChatGPT Work update to 0.3.1 and live provider requests: NOT_RUN.

## 0.3.0 source (2026-10-29)

Execution environment: Claude Code cloud container, Linux, Python 3.13.17, Pillow 12.3.0, FFmpeg present. `python3 tools/check.py`: PASS (runtime 19, providers 7, package 4, contract 17 tests; reproducible ZIP; extracted runtime status). Hosted ChatGPT Work update to 0.3.0: pending (owner step, see the Creative Studio repository's update prompt). Installed-client tests in Claude and Codex: NOT_RUN. Live provider requests: NOT_RUN.

## Initial standalone import (0.2.1)

Date: 2026-10-28. Execution environment: ChatGPT Work, Linux, Python 3.12.14, Pillow 12.3.0, PyYAML 6.0.3.

| Check | Result |
| --- | --- |
| All 61 plugin files compared to Plugin Creator source | PASS, exact bytes |
| Current hosted release rechecked after import | PASS, still 0.2.1 and the same release ID |
| Runtime regression suite | PASS, 19 tests |
| Provider regression suite | PASS, 7 tests |
| Package regression suite using this repository's marketplace | PASS, 4 tests |
| JSON, skill/agent YAML, manifest/version agreement and local Markdown links | PASS |
| Deterministic single-plugin ZIP, byte comparison and CRC | PASS |
| Runtime `status` from the ZIP extracted outside the repository | PASS, 14 providers, network NOT_RUN |
| GitHub-hosted CI execution | Not established by this local check |
| Fresh installed-client execution in Claude or Codex | NOT_RUN |
| Live provider searches and downloads in this extraction task | NOT_RUN |

The 30 regression tests use fixtures, mocks and temporary files. Logs describing synthetic HTTP requests come from mocked-client tests. They do not establish current live service availability or per-asset reuse clearance. Existing provider dossiers retain their historical evidence dates; this import does not renew that evidence.

Run `python3 tools/check.py` from the repository root to reproduce the source, test and packaging checks. The standalone wrapper does not alter the imported runtime or skill.
