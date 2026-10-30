# Installation and local use

This repository contains only FrameCore Open Assets. Creative Studio, FrameCut and FrameCore Works Toolbox are optional integrations; this plugin never requires or calls them.

## Requirements

- Python 3.10 or newer and a shell/code execution tool.
- Pillow for decoding images and texture packages.
- FFmpeg and FFprobe for decoding audio/video.
- Network access to the selected provider's documented domains for live requests.

Run the bundled `status` command before sourcing media. Install missing dependencies only with the user's authorization. Tests and packaging need the versions listed in `requirements-dev.txt`; FFmpeg is not needed for the existing offline test suite.

## ChatGPT Work

1. Build the single-plugin archive with `python3 tools/package.py` where code execution has this repository; otherwise build it from files read as text ([Update without a ZIP](#update-without-a-zip-owner-decision-2026-10-29)). Never ask the user to upload a ZIP.
2. In Plugin Creator, resolve any existing **FrameCore Open Assets** plugin before saving. Inspect its current release and files. Update that existing identity with its current release guard; create a new plugin only when the user wants an installation and none exists.
3. Give Plugin Creator the generated ZIP from code execution, not a ZIP of the whole repository. Verify the returned release, component diagnostics and stored file contents.
4. Resolve the installed `open-assets` skill in the actual host, then run its runtime `status`.

The hosted release imported into this repository is 0.2.1 (receipt in `provenance/`). Source 0.3.0 updates that existing identity with its release guard; never create a duplicate. After the hosted update, read back the stored files and record a new receipt.

Ordinary ChatGPT without code execution or permitted network access can plan the work but cannot execute the CLI. Work execution evidence does not establish readiness in another host.

## Update without a ZIP (owner decision 2026-10-29)

Installation and updates run on their own: never download a release ZIP, never ask the owner to attach or upload a
file. ChatGPT Work has no network in code execution and its update tool takes no URL. It reads repository files as
text through the GitHub connector, but that text cannot be moved into code execution (Work attempt 2026-10-30: 31
of 31 files read, 0 transferred). So the files go from the connector straight to Plugin Creator, and code execution
only checks what was saved:

1. Resolve `main` to one full commit. List `plugins/framecore-open-assets/` recursively at that commit through the connector; each
   entry carries its git blob `sha` and `size` (NEW). For an update, list the commit that released the saved version
   too (the commit named "Open Assets <version>" in the history; OLD).
2. Decide the files to write: for a first installation every file; for an update every path whose NEW hash differs
   from OLD or that is new, plus the delete paths (in OLD, not in NEW, present in the saved plugin). A saved file
   that differs from both OLD and NEW is a private edit: merge it, never overwrite it silently.
3. Read each of those files through the connector at the pinned commit and give its exact text to Plugin Creator as
   that path's file content; create the plugin (first installation, after checking no FrameCore Works Toolbox or
   Open Assets identity exists) or update the existing one with the delete paths under the current release guard.
4. Check the saved plugin in code execution: save `tools/hosted_update.py` there (its text typed in, or read from the saved
   plugin where present), write EXPECT as {path: git blob sha} for the written files from NEW, then run
   `python3 hosted_update.py verify --expect EXPECT.json --saved SAVED_DIR --absent <delete paths>`. A mismatch
   names the path: write that file again from the connector, unchanged. Report save and verification separately.
   Without the script, this prints each saved file's git blob hash to compare with NEW:
   `python3 -c "import hashlib,pathlib,sys;[print(p,hashlib.sha1(b'blob %d\0'%len(d)+d).hexdigest()) for p in sys.argv[1:] for d in [pathlib.Path(p).read_bytes()]]" <paths>`.

Where code execution can read the whole repository (a host with network), `hosted_update.py plan` and `pack` build
the same update as a verified delta ZIP instead.

## Codex

Use the host's native plugin installation/discovery flow with the complete `plugins/framecore-open-assets` directory or its generated archive, depending on what that host accepts. Keep `plugin.json`, `.codex-plugin/plugin.json`, the skill, scripts, provider registry and references together. Do not install only `SKILL.md` into personal skills: its relative runtime would be missing.

After installation, resolve the actual plugin directory and run `python3 <plugin-directory>/scripts/runtime.py status`. Use `--host codex` only when running in Codex. Availability of a native plugin installer depends on the host; direct CLI use remains possible in a local checkout with the requirements above.

## Claude Code

For users with access to this GitHub repository, run inside Claude Code:

```text
/plugin marketplace add FrameCoreWorks/framecore-open-assets
/plugin install framecore-open-assets@framecore-open-assets
```

The marketplace name is `framecore-open-assets`; it contains exactly one plugin with the same technical name. You can also add an authenticated local checkout as the marketplace. A private repository requires GitHub access in the installing environment.

After installation, resolve its installed runtime and run `status`. Use `--host claude_code` for actual Claude Code execution. The official [marketplace documentation](https://code.claude.com/docs/en/plugin-marketplaces) describes repository and local-path installation.

## Claude apps

If the workspace supports repository marketplaces, add this repository and select **FrameCore Open Assets**. Account policy and available code/network tools determine whether the runtime can execute. Use `--host claude_apps` only for execution in a Claude app. This repository does not claim that an app installation or runtime was tested.

## Direct CLI use

From the repository root:

```bash
python3 plugins/framecore-open-assets/scripts/runtime.py status
```

For a real sourcing task, replace the placeholders with the executing host, actual model identifier and writable paths **outside the repository**:

```bash
python3 plugins/framecore-open-assets/scripts/runtime.py \
  --state /absolute/project/open-assets-state \
  search --host ACTUAL_HOST --model ACTUAL_MODEL \
  --provider met --category graphics --query sunflowers --limit 3 \
  --out /absolute/project/assets/search.json
```

Review the chosen source, licence, creator, variant and warnings. The first selected asset for a host/provider/category uses `verify`, which both downloads it and writes a provenance sidecar:

```bash
python3 plugins/framecore-open-assets/scripts/runtime.py \
  --state /absolute/project/open-assets-state \
  verify --host ACTUAL_HOST --model ACTUAL_MODEL \
  --results /absolute/project/assets/search.json --index 0 --variant 0 \
  --out /absolute/project/assets/sunflowers.jpg
```

Do not repeat a successful `verify` as a second download. Consult the [skill](plugins/framecore-open-assets/skills/open-assets/SKILL.md) and [contract](plugins/framecore-open-assets/skills/open-assets/references/contract.md) for rights review, expiry, limits and failures.
