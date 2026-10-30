# FrameCore Open Assets

A standalone media-sourcing companion for Claude, ChatGPT Work and Codex. One shared skill and
Python runtime, three synchronized manifests, and one marketplace entry. It hands source records to
any consumer that reads them, such as Creative Studio, FrameCut or Earshot through FrameCore Works
Toolbox (which imports eligible audio); none of them is required.

Search official free APIs without signup or keys, inspect each asset's rights, and save a decoded
file with source, creator, licence, attribution, hash and verification evidence. Public provider
requests leave the executing host; no client media is uploaded. There is no remote MCP server,
paid generation, account setup or browser scraping.

## Provider coverage

Fourteen executable providers: Wikimedia Commons, The Met, Cleveland, Rijksmuseum (PDM/CC0 images), Library of Congress (dedicated Gottlieb photographs), NASA (photos/video), LibriVox, Finna, Wellcome, ambientCG, PhyloPic, Poly Haven, SMK and SFXMint. Each provider has its own documented module and rights gate. NASA/LibriVox require item/use-specific review; SA requires deliberate acceptance.

Only confirmed provider/category paths are included. See [provider details](skills/open-assets/references/provider-index.md). There is no arbitrary provider-count cap. Broad music, recorded SFX and contemporary stock footage remain gaps.

## Installation and capabilities

Use the complete host procedure in the [installation guide](https://github.com/FrameCoreWorks/framecore-open-assets/blob/main/INSTALL.md)
(Claude, ChatGPT Work and Codex). The plugin itself uses Python's standard
library. Image verification also needs Pillow; audio/video verification needs FFmpeg and FFprobe.
Ask before installing missing dependencies. No model downloads are needed.

In Claude Code 2.1.275 or later, one line adds the marketplace and installs the plugin:

```text
/plugin install framecore-open-assets --marketplace FrameCoreWorks/framecore-open-assets
```

The skill is readable in compatible clients; execution requires a shell/code tool and permitted
network. An ordinary chat without those capabilities can plan but cannot claim searches/downloads.
Provider verification is local to the actual host/category/runtime and expires after one day.
No Work test proves Claude Code, Claude apps or Codex behavior.

## Developer checks

Run `python3 tests/runtime_test.py`, `python3 tests/providers_test.py`, `python3 tests/package_test.py`,
`python3 tests/contract_test.py` and `python3 tests/network_test.py` from this plugin directory. The repository's full check runs all five. Tests cover observed API response shapes, rights gates,
provenance tampering, HTTP blocks/cache/budgets, actual image decoding and package discovery.
No test installs upstream software or makes a provider request. Live CLI tests need separate
authorization and are not part of these checks.

Callers that coordinate several plugins can read [capabilities.json](capabilities.json) and ask for a
`framecore-task-result/1` envelope with `--envelope-out`; the shared schema is in
[contracts/framecore-task.schema.json](contracts/framecore-task.schema.json).

Operational examples and complete input/output/error contracts are in the
[Open Assets skill](skills/open-assets/SKILL.md) and [runtime contract](skills/open-assets/references/contract.md).
Do not save downloaded media, runtime state or credentials inside this package or commit them.
