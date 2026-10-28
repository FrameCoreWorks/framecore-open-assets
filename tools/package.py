#!/usr/bin/env python3
"""Build one portable plugin; never include repository or operational state."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/framecore-open-assets'
TOP_FILES = {'plugin.json', 'providers.json', 'README.md', 'CHANGELOG.md', 'LICENSE', 'NOTICE'}
TOP_DIRS = {'.claude-plugin', '.codex-plugin', 'skills', 'scripts', 'tests'}


def source_files():
    result = {}
    for path in sorted(PLUGIN.rglob('*')):
        relative = path.relative_to(PLUGIN)
        if '__pycache__' in relative.parts or path.suffix in {'.pyc', '.pyo'}:
            continue
        if path.is_symlink():
            raise ValueError(f'Symlinks are not package files: {relative}')
        if path.is_dir():
            continue
        if (len(relative.parts) == 1 and relative.name not in TOP_FILES) or (
            len(relative.parts) > 1 and relative.parts[0] not in TOP_DIRS
        ):
            raise ValueError(f'Unexpected package path: {relative}')
        if path.suffix not in {'.py', '.json', '.md', '.yaml'} and relative.name not in {'LICENSE', 'NOTICE'}:
            raise ValueError(f'Unexpected package file type: {relative}')
        result[relative.as_posix()] = path.read_bytes()
    return result


def build(output_dir):
    version = json.loads((PLUGIN / 'plugin.json').read_text())['version']
    output_dir = Path(output_dir).resolve()
    if output_dir == PLUGIN or PLUGIN in output_dir.parents:
        raise ValueError('Write release archives outside the plugin directory')
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f'framecore-open-assets-{version}.zip'
    files = source_files()
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, contents in files.items():
            entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, contents, compresslevel=9)
    with zipfile.ZipFile(target) as archive:
        if archive.namelist() != list(files) or archive.testzip() is not None:
            raise ValueError('Archive inventory or CRC mismatch')
        for name, contents in files.items():
            if archive.read(name) != contents:
                raise ValueError(f'Archive bytes differ: {name}')
    checksum = hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix('.zip.sha256').write_text(f'{checksum}  {target.name}\n')
    return target


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'dist')
    print(build(parser.parse_args().output_dir))
