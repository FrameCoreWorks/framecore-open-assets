# Source synchronization and standalone extraction

Observed on 2026-10-28 through Plugin Creator, using all pages of the current source inventory.

| Input | Version | Role |
| --- | --- | --- |
| User-uploaded ZIP | 0.1.1 | Older comparison baseline |
| Current ChatGPT Work plugin | 0.2.1 | Authoritative imported source |
| Standalone repository plugin | 0.2.1 | Exact copy of all 61 current source files |

## Changes from 0.1.1

The current release adds executable Finna, Library of Congress, Rijksmuseum and SMK adapters. It distributes 14 providers and 23 confirmed provider/category paths. Unused AIC, Internet Archive, ccMixter and Gallica dossiers are no longer packaged. NASA exposes confirmed photos/video paths. Updated regression tests cover provider/category-bound readiness proofs, pacing, localized licence URLs, rights wording, image-specific rights and media-type mismatch.

The import preserves current rights gates, signatures, bounded network handling and optional Studio/Earshot handoffs (since 0.3.0 the Earshot consumer is FrameCore Works Toolbox). This comparison records implementation differences; it is not a new live-provider test or a legal clearance of third-party media.

## Standalone boundary

All runtime imports and provider references resolve inside the plugin. Its Python code does not import Creative Studio, Earshot or FrameCut. The original package test expects a marketplace two levels above the plugin, so this repository provides its own one-entry catalogue at that location. Installation, development, CI and packaging instructions are now maintained here independently.

All 61 imported plugin files are unchanged, including default prompts, manifests, tests and the original repository URL in the Claude manifest and HTTP User-Agent. Those historical URLs are informational and do not load runtime code. They were retargeted to this repository in 0.3.0. Root documentation supersedes the imported README's monorepo installation links for use of this repository.

The receipt in [provenance](../provenance/chatgpt-work-0.2.1.json) includes the exact hosted release ID and every file's SHA-256. The 0.1.1 input archive SHA-256 is `f4c23332ac644f52ba267bb8007f5162a6ebdca02560993fae9400d5dd63cf30`.

No installed plugin was republished, duplicated or downgraded during this import. The existing Creative Studio repository and its plugin are separate projects; this extraction does not alter them. There is no automatic GitHub-to-Plugin-Creator deployment.

## File comparison

### Added (5)

- `scripts/providers/finna.py`
- `scripts/providers/loc.py`
- `scripts/providers/rijks.py`
- `scripts/providers/smk.py`
- `tests/providers_test.py`

### Removed (4)

- `skills/open-assets/references/providers/aic.md`
- `skills/open-assets/references/providers/archive.md`
- `skills/open-assets/references/providers/ccmixter.md`
- `skills/open-assets/references/providers/gallica.md`

### Changed (20)

- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`
- `CHANGELOG.md`
- `README.md`
- `plugin.json`
- `providers.json`
- `scripts/core.py`
- `scripts/providers/nasa.py`
- `scripts/runtime.py`
- `skills/open-assets/SKILL.md`
- `skills/open-assets/references/contract.md`
- `skills/open-assets/references/provider-index.md`
- `skills/open-assets/references/providers/finna.md`
- `skills/open-assets/references/providers/librivox.md`
- `skills/open-assets/references/providers/loc.md`
- `skills/open-assets/references/providers/nasa.md`
- `skills/open-assets/references/providers/rijks.md`
- `skills/open-assets/references/providers/smk.md`
- `tests/package_test.py`
- `tests/runtime_test.py`
