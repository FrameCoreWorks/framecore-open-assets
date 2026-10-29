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

The update runs on its own: never download a release ZIP, never ask the owner to attach or upload a file. ChatGPT
Work has no network in code execution and its update tool does not take a URL, but it reads repository files as
text through the GitHub connector, so the update is built there:

1. Resolve `main` to one full commit. List `plugins/framecore-open-assets/` recursively at that commit through the connector;
   each entry carries its git blob `sha` and `size`. Save the listing as `{"tree": [{"path", "type": "blob",
   "sha", "size"}]}` (NEW). Do the same at the commit that released the saved version (the commit named "Open Assets <version>" in the history) for OLD; without
   it the baseline is unknown and nothing is deleted.
2. Read `tools/hosted_update.py` at the pinned commit through the connector and save it in code execution (standard library
   only, no network).
3. With the saved plugin's files in code execution:
   `python3 hosted_update.py plan --new NEW.json --old OLD.json --prefix plugins/framecore-open-assets --saved SAVED_DIR --out plan.json`.
4. Read every `fetch` path from `plugins/framecore-open-assets/<path>` through the connector and save it unchanged under the same
   relative path (a binary file as `<path>.b64` with base64 content).
5. `python3 hosted_update.py pack --new NEW.json --prefix plugins/framecore-open-assets --plan plan.json --files FETCHED_DIR --out delta.zip`
   checks every file against its git blob hash and writes `delta.zip` plus `delta.zip.json`. A mismatch stops it
   with the path; read that file again unchanged.
6. Pass `delta.zip` from code execution to the update tool with the plan's `delete_paths` under the current
   release guard (if it cannot take a code-execution file, pass the same verified files as file contents). Merge
   `review` paths by hand. Read back the affected files and confirm the deleted paths are absent.

A first installation follows the same steps without `--old` and `--saved`: the plan then reads every file.

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
