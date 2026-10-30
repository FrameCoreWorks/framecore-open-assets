# Installation and local use

This repository contains only FrameCore Open Assets. Creative Studio, FrameCut and FrameCore Works Toolbox are optional integrations; this plugin never requires or calls them.

## Requirements

- Python 3.10 or newer and a shell/code execution tool.
- Pillow for decoding images and texture packages.
- FFmpeg and FFprobe for decoding audio/video.
- Network access to the selected provider's documented domains for live requests. `runtime.py reach` checks it; in a cloud container follow [Running Open Assets in a cloud container](docs/CLOUD_NETWORK.md).

Run the bundled `status` command before sourcing media. Install missing dependencies only with the user's authorization. Tests and packaging need the versions listed in `requirements-dev.txt`; FFmpeg is not needed for the existing offline test suite.

## ChatGPT Work

1. Build the single-plugin archive with `python3 tools/package.py` where code execution has this repository; otherwise build it from files read as text ([Update without a ZIP](#update-without-a-zip-owner-decision-2026-10-29)). Never ask the user to upload a ZIP.
2. In Plugin Creator, resolve any existing **FrameCore Open Assets** plugin before saving. Inspect its current release and files. Update that existing identity with its current release guard; create a new plugin only when the user wants an installation and none exists.
3. Give Plugin Creator the generated ZIP from code execution, not a ZIP of the whole repository. Verify the returned release, component diagnostics and stored file contents.
4. Resolve the installed `open-assets` skill in the actual host, then run its runtime `status`.

The hosted release imported into this repository is 0.2.1 (receipt in `provenance/`). Source 0.4.0 updates that existing identity with its release guard; never create a duplicate. After the hosted update, read back the stored files and record a new receipt.

Ordinary ChatGPT without code execution or permitted network access can plan the work but cannot execute the CLI. Work execution evidence does not establish readiness in another host.

## Update without a ZIP (owner decision 2026-10-29)

Installation and updates run on their own: never download a release ZIP, never ask the owner to attach or upload a
file. What ChatGPT Work's tools allow (attempts of 2026-10-30): Plugin Creator's `create_plugin` and `update_plugin`
take only `archive`, an absolute path to a ZIP in code execution (a data URL is refused with `INVALID_ARGUMENT`);
code execution has no network (github.com does not resolve); the GitHub connector returns file text to the model
but writes no file into code execution. So the model itself writes each file's text into code execution, checks
it against the git blob hashes and zips it there:

1. Resolve `main` to one full commit. List `plugins/framecore-open-assets/` recursively at that commit through the connector; each
   entry carries its git blob `sha` and `size` (NEW). Search Plugin Creator's saved plugins for FrameCore Open
   Assets: none means a first installation; otherwise this is an update of that identity (list the commit that released the saved
   version, the commit named "Open Assets <version>" in the history, as OLD).
2. Choose the files: a first installation takes every file; an update takes every path whose NEW hash differs from
   OLD or that is new, deletes the paths in OLD but not in NEW, and merges any private edit by hand.
   The plugin's `tests/` folder (20 files, 108 KB) is not needed at run time and may be left out (46 files and
   141 KB remain).
3. Read each chosen file through the connector and write its exact text in code execution under
   `/mnt/data/open-assets/<path>` (`pathlib.Path(...).write_text(text, encoding='utf-8')`; for a long file several
   cells that append in order). Keep every character, including the final newline. Write
   `/mnt/data/expect.json` as {path: git blob sha} for the chosen files, copied from NEW.
4. Check and zip in one cell; it writes the ZIP only when every file matches:

   ```python
   import hashlib,json,pathlib,zipfile
   R=pathlib.Path('/mnt/data/open-assets');E=json.load(open('/mnt/data/expect.json'))
   bad=[p for p,h in E.items() if not (R/p).is_file() or hashlib.sha1(b'blob %d\0'%len(d:=(R/p).read_bytes())+d).hexdigest()!=h]
   print('BAD',bad) if bad else print('OK',len(E))
   if not bad:
       with zipfile.ZipFile('/mnt/data/open-assets.zip','w',zipfile.ZIP_DEFLATED) as z:[z.write(R/p,p) for p in sorted(E)]
   ```

   For each path in `BAD`, read the file again from the connector and rewrite it unchanged; never patch it by guess.
5. First installation: `create_plugin(archive="/mnt/data/open-assets.zip")`. Update: `update_plugin` with the same
   archive, the delete paths and the current release guard; an update overlays the saved release, so a ZIP of only
   the changed files is enough. Read back the saved manifests and skill, and report save and checks separately.

Where code execution can read the whole repository (a host with network), the repository's own package script, or
`hosted_update.py plan` and `pack`, build the same archive directly.

## Codex

Use the host's native plugin installation/discovery flow with the complete `plugins/framecore-open-assets` directory or its generated archive, when that host offers one. Keep `plugin.json`, `.codex-plugin/plugin.json`, the skill, scripts, provider registry and references together. Do not install only `SKILL.md` into personal skills: its relative runtime would be missing.

### Native entry with the complete bundle

Without a native plugin installer, use the same direct-source pattern as Creative Studio and Toolbox. Python 3.10+ is sufficient. On the user's installation request, resolve the actual Codex skill scope (`.agents/skills` for the selected project or `~/.agents/skills` for the user) and a persistent bundle location outside every skill-discovery root. Inspect active scopes for an existing `open-assets` skill or plugin first and preserve existing or edited content. From a checkout at a verified full commit, the assistant substitutes absolute paths:

```sh
python3 tools/install_codex.py plan --skills-dir "<skills-dir>" --bundle-dir "<bundle-dir>" --source-commit "<40-character-commit>"
python3 tools/install_codex.py install --skills-dir "<skills-dir>" --bundle-dir "<bundle-dir>" --source-commit "<40-character-commit>"
python3 tools/install_codex.py verify --skills-dir "<skills-dir>" --bundle-dir "<bundle-dir>" --source-commit "<40-character-commit>"
```

The helper makes no network requests. It copies the complete plugin into the bundle, creates one native `open-assets` entry pointing to the bundled skill, and records file hashes and the source commit in `installation.json`. `plan` writes nothing; identical repeats are read-only; conflicting, edited or partial installations are rejected and left untouched. A receipt proves file installation, not host activation: refresh the Codex skills view or start a new session. To update, choose a new versioned bundle path and replace only the verified previous entry under the user's update request.

After installation, run `python3 <bundle-dir>/scripts/runtime.py status --host codex` (only when actually running in Codex; plain `status` reports every host). Direct CLI use also works in a local checkout with the requirements above.

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
