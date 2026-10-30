#!/usr/bin/env python3
"""Install one native Codex skill entry backed by the complete plugin bundle; no network."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import shutil

from package import PLUGIN

NAME = 'open-assets'
SKIP = {'__pycache__'}


def reject_symlinks(path):
    for candidate in (path, *path.parents):
        if candidate.is_symlink():
            raise ValueError('Refusing symlink destination: ' + str(candidate))


def overlaps(a, b):
    return a == b or a in b.parents or b in a.parents


def inventory(directory):
    files = {}
    for path in sorted(directory.rglob('*')):
        relative = path.relative_to(directory)
        if SKIP.intersection(relative.parts) or path.suffix in {'.pyc', '.pyo'}:
            continue
        if path.is_symlink():
            raise ValueError('Refusing symlink: ' + str(relative))
        if path.is_file():
            files[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def entry_text(bundle, description):
    runtime = bundle / 'scripts' / 'runtime.py'
    return ('---\nname: ' + NAME + '\ndescription: ' + json.dumps(description) + '\n---\n\n'
            '# ' + NAME + '\n\n'
            f'Read `{bundle / "skills" / NAME / "SKILL.md"}` and follow its instructions.\n'
            'Resolve all references and scripts from that bundled skill location.\n'
            f'Check readiness with `python3 {shlex.quote(str(runtime))} status --host codex`. Use the actual\n'
            'host and model, and the user\'s language. Installed files do not establish\n'
            'provider readiness.\n')


def run(action, plugin, skills, bundle, source_commit):
    if action not in {'plan', 'install', 'verify'}:
        raise ValueError('Unknown action')
    if not re.fullmatch('[0-9a-f]{40}', source_commit):
        raise ValueError('Use a verified full source commit')
    plugin = Path(plugin).resolve()
    repo = plugin.parents[1]
    for path in (skills, bundle):
        if not path.is_absolute() or any(c in str(path) for c in ('\n', '\r', '`')):
            raise ValueError('Use absolute destination paths without line breaks or backticks')
        reject_symlinks(path)
    skills, bundle = skills.resolve(), bundle.resolve()
    if overlaps(skills, bundle) or overlaps(repo, bundle) or overlaps(repo, skills):
        raise ValueError('Keep destinations separate and outside the source repository')
    target = skills / NAME
    reject_symlinks(target)
    manifest = json.loads((plugin / 'plugin.json').read_text())
    files = inventory(plugin)
    entry = entry_text(bundle, manifest['description'])
    receipt = {'plugin': manifest['name'], 'version': manifest['version'],
               'source_commit': source_commit, 'bundle_dir': str(bundle), 'files': files}

    def verify():
        try:
            reject_symlinks(target / 'SKILL.md')
            reject_symlinks(target / 'installation.json')
            if inventory(bundle) != files or (target / 'SKILL.md').read_text() != entry:
                raise ValueError('Installation differs from source; preserve and inspect edits')
            if json.loads((target / 'installation.json').read_text()) != receipt:
                raise ValueError('Installation receipt differs from requested source')
            if {p.name for p in target.iterdir()} != {'SKILL.md', 'installation.json'}:
                raise ValueError('Entry contains additional local content; inspect it')
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError('Partial or unreadable installation; inspect before recovery') from error

    result = {'status': 'FILES_VERIFIED', 'version': manifest['version'],
              'files': len(files), 'host_activation': 'NOT_RUN'}
    if action == 'verify':
        verify()
        return result
    if target.exists() or bundle.exists():
        verify()
        return {**result, 'status': 'already_up_to_date', 'writes': 0}
    if action == 'plan':
        return {**result, 'status': 'READY', 'writes': 0, 'entry': str(target), 'bundle': str(bundle)}
    # Exclusive creation: never overwrite or clean up existing user content.
    skills.mkdir(parents=True, exist_ok=True)
    bundle.parent.mkdir(parents=True, exist_ok=True)
    bundle.mkdir(exist_ok=False)
    for relative in files:
        destination = bundle / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(plugin / relative, destination)
    target.mkdir(exist_ok=False)
    (target / 'SKILL.md').write_text(entry, encoding='utf-8')
    (target / 'installation.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    verify()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['plan', 'install', 'verify'])
    parser.add_argument('--skills-dir', type=Path, required=True)
    parser.add_argument('--bundle-dir', type=Path, required=True)
    parser.add_argument('--source-commit', required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.action, PLUGIN, args.skills_dir, args.bundle_dir, args.source_commit), indent=2))


if __name__ == '__main__':
    main()
