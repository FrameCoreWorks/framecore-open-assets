# FrameCore Open Assets

Standalone asset-sourcing plugin for **ChatGPT Work, Codex and Claude**, maintained by FrameCore Works. Find media through documented public APIs, check each asset's rights, and download verified files with source and attribution records.

**Current plugin version: 0.4.1** (source; the hosted ChatGPT Work release is still 0.2.1 until it is updated, see [validation](docs/VALIDATION.md)). This repository adds its own installation guide, single-plugin marketplace, validation, reproducible packaging and CI. Creative Studio, FrameCut and FrameCore Works Toolbox (its built-in Earshot capability imports eligible audio) are optional consumers of its provenance records; none is required to run this plugin. Callers can ask for a shared `framecore-task-result/1` envelope and read `capabilities.json` to discover what it offers.

## Start here

- [Installation and local use](INSTALL.md)
- [Provider coverage](plugins/framecore-open-assets/skills/open-assets/references/provider-index.md)
- [Commands and output contract](plugins/framecore-open-assets/skills/open-assets/references/contract.md)
- [Development and release workflow](CONTRIBUTING.md)
- [Changes from the uploaded 0.1.1 package](docs/SOURCE_SYNC.md)
- [Plugin changelog](plugins/framecore-open-assets/CHANGELOG.md)

From the repository root, inspect local capabilities without a network request:

```bash
python3 plugins/framecore-open-assets/scripts/runtime.py status
```

Python 3.10+ runs the CLI. Pillow verifies images and texture packages; FFmpeg and FFprobe verify audio/video. Search and download also require permitted network access; `runtime.py reach` shows which providers this environment can connect to, and [cloud containers](docs/CLOUD_NETWORK.md) lists the hosts to allow. Installation alone does not establish provider readiness.

### If search fails

Most failed searches are a network policy, not a broken plugin. Run:

```bash
python3 plugins/framecore-open-assets/scripts/runtime.py reach
```

- `reachable` for every provider: the network is fine; retry, or try another provider or category.
- `blocked` (or a search error `network_blocked`): your environment refuses those hosts. Add the `allowlist` that `reach` prints to the environment's allowed domains (`runtime.py domains` prints the same list); [cloud containers](docs/CLOUD_NETWORK.md) shows where for Claude Code cloud. Then start a new session.
- `unreachable` or `unknown` for one provider: that provider is down or slow; the others still work.

## Providers and boundaries

The release contains 14 providers and 23 provider/category combinations: Wikimedia Commons, The Met, Cleveland Museum of Art, Rijksmuseum, Library of Congress, NASA, LibriVox, Finna, Wellcome Collection, ambientCG, PhyloPic, Poly Haven, SMK and SFXMint. Each has a separate adapter and rights rules. Broad music, recorded SFX and contemporary stock footage remain limited.

The runtime preserves source, creator, licence, attribution, file hash and decoder evidence. It blocks unknown or unsupported rights and checks the current host before routine downloads. Provider eligibility is separate from permission to reuse an individual asset. See the skill and provider dossiers for the operational rules.

There is no hosted MCP server or API credential requirement. Public provider requests leave the executing host; the runtime does not upload client media. Keep downloaded assets, cache, signing keys and readiness records outside the plugin and Git repository.

## Repository layout

| Path | Purpose |
| --- | --- |
| `plugins/framecore-open-assets/` | Complete installable plugin, independent of any sibling project |
| `.claude-plugin/marketplace.json` | This repository's single-plugin catalogue |
| `tools/check.py` | Source, metadata, reference and archive validation plus existing tests |
| `tools/package.py` | Deterministic single-plugin ZIP builder |
| `provenance/` | Immutable import receipt and SHA-256 file inventory |
| `.github/workflows/ci.yml` | Offline test and packaging checks on Ubuntu/Python 3.12 |

The nested plugin directory preserves the established packaging contract. It is not a submodule and does not fetch Creative Studio. The imported plugin's historical documentation and repository URL still identify its original home; the root documentation here describes this standalone repository. Future plugin releases can update those fields with a coordinated version bump.

## Validate and package

```bash
python3 tools/check.py
python3 tools/package.py
```

The ZIP in `dist/` contains one plugin at the archive root, including its hidden compatibility manifests. It excludes the marketplace, CI, Git history and development output. CI uses the same local check. Live provider requests are intentionally separate from automated tests.

## Licence

Original FrameCore Works code: [Apache-2.0](LICENSE). See [NOTICE](NOTICE). Provider data and media retain their own rights; the code licence does not relicense downloaded assets.
