# Validation

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
