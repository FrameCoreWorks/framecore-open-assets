# Development and releases

## One independently maintained plugin

Edit `plugins/framecore-open-assets/` in this repository. Its runtime, provider registry, dossiers and fixtures are local; no Creative Studio checkout or service is needed. Consumers receive downloaded media and `.asset.json` sidecars through the existing contract.

The repository starts from the current ChatGPT Work 0.2.1 release. `provenance/chatgpt-work-0.2.1.json` records the exact imported bytes and release identity. Keep this receipt immutable. For this version, validation refuses any undocumented source drift. For a future version, retain the receipt as historical evidence and record the new source/release relationship in the changelog.

## Local checks

Use a virtual environment if dependencies are missing; install `requirements-dev.txt` only within the user's authorization. Then run:

```bash
python3 tools/check.py
python3 tools/package.py
```

The check runs all three existing test suites and validates manifests, skill YAML, local Markdown links, the standalone marketplace, baseline hashes and archive contents. Tests use temporary directories and fixtures, not live provider APIs. CI runs the same command on Ubuntu/Python 3.12. Other Python versions, Windows, installed clients and live provider availability require separate evidence.

The imported package test expects a marketplace two directories above the plugin. This repository supplies that catalogue itself; it does not depend on the original monorepo. Run the complete check from this checkout. A package-only archive is installable without the development marketplace.

## New providers and runtime changes

Keep the registry, adapter, supported categories, provider dossier and tests consistent. Verify official API and rights information before enabling a provider; record source URLs and review dates. Do not turn metadata licences into image/audio/video permission. Preserve request limits, host verification, provenance, rights gates and failure reporting.

Do not commit assets downloaded during tests, credentials, signed readiness records, caches or user content. Live provider tests require task-specific authorization and should write outside the repository. Describe the actual host and observed limits instead of treating a fixture test as a live success.

## Release checklist

1. Make a focused branch and describe the intended change.
2. Bump all three plugin manifests, `scripts/core.py`'s version, the standalone marketplace version and package-test expectations together. Preserve all plugin-level default prompts unless their change is requested.
3. Update the plugin changelog, relevant documentation and meaningful regression tests.
4. Run `python3 tools/check.py` and build the single-plugin ZIP. Review the diff and archive inventory.
5. Commit and push the reviewed source to this repository. Tag an approved release only after validation; the initial import does not create an automatic release or deployment.
6. When a ChatGPT Work update is requested, inspect the currently installed release through Plugin Creator, reconcile changes and update its existing plugin identity with `expected_release_id`. Read back affected source and preserve unrelated metadata and visibility.
7. When a Creative Studio marketplace update is requested, use a separate reviewed change to that repository. Do not silently overwrite its vendored companion or install two copies into the same host.

GitHub commits do not automatically update a Plugin Creator installation. Future releases should also replace the imported historical repository URLs with this repository's URL as part of the coordinated plugin version change.
