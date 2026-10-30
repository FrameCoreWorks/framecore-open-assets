#!/usr/bin/env python3
"""Validate the standalone repository and run all imported offline tests."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile

import yaml

from package import ROOT, PLUGIN, build, source_files


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    files = source_files()
    for name, content in files.items():
        if name.endswith('.json'):
            json.loads(content)
        if name.endswith('.yaml'):
            require(isinstance(yaml.safe_load(content), dict), f'Invalid YAML mapping: {name}')
    manifests = [json.loads(files[p]) for p in ('plugin.json', '.codex-plugin/plugin.json', '.claude-plugin/plugin.json')]
    version = manifests[0]['version']
    require(all(m['version'] == version for m in manifests), 'Manifest versions differ')
    require(re.fullmatch(r'\d+\.\d+\.\d+', version), 'Expected release SemVer')
    interface = manifests[0]['extensions']['com.openai']['interface']
    require(isinstance(interface['capabilities'], list), 'Capabilities must be an array')
    require(interface == manifests[1]['interface'], 'Portable and Codex presentation differ')
    skill = files['skills/open-assets/SKILL.md'].decode('utf-8')
    frontmatter = yaml.safe_load(skill.split('---', 2)[1])
    require(frontmatter['name'] == 'open-assets' and isinstance(frontmatter['description'], str), 'Invalid skill metadata')
    require("VERSION = '" + version + "'" in files['scripts/core.py'].decode(), 'Runtime version differs')
    market = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
    require(market['name'] == 'framecore-open-assets', 'Wrong standalone marketplace name')
    require(len(market['plugins']) == 1, 'Marketplace must contain only this plugin')
    entry = market['plugins'][0]
    require(entry['name'] == 'framecore-open-assets' and entry['version'] == version, 'Marketplace identity differs')
    require((ROOT / entry['source']).resolve() == PLUGIN, 'Marketplace points outside this plugin')
    receipt = json.loads((ROOT / 'provenance/chatgpt-work-0.2.1.json').read_text())
    if version == receipt['plugin_version']:
        hashes = {p: hashlib.sha256(data).hexdigest() for p, data in files.items()}
        require(hashes == receipt['sha256'], '0.2.1 source drift: bump version for intentional changes')
        print(f'Hosted source match: {len(hashes)} files, exact bytes', flush=True)
    for path in ROOT.rglob('*.md'):
        if '.git' in path.parts or 'dist' in path.parts:
            continue
        for link in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if '://' not in link and not link.startswith('#'):
                require((path.parent / link.split('#')[0]).exists(), f'Broken local link: {path}: {link}')
    workflow = yaml.safe_load((ROOT / '.github/workflows/ci.yml').read_text())
    require(workflow['permissions'] == {'contents': 'read'}, 'CI should not write repository contents')
    for test in ('runtime_test.py', 'providers_test.py', 'package_test.py', 'contract_test.py', 'network_test.py'):
        subprocess.run([sys.executable, str(PLUGIN / 'tests' / test)], cwd=PLUGIN, check=True)
    subprocess.run([sys.executable, str(ROOT / 'tools' / 'install_codex_test.py')], cwd=ROOT, check=True)
    with tempfile.TemporaryDirectory() as temp:
        one = build(Path(temp) / 'one')
        two = build(Path(temp) / 'two')
        require(one.read_bytes() == two.read_bytes(), 'Archive is not reproducible')
        with zipfile.ZipFile(one) as archive:
            require('plugin.json' in archive.namelist(), 'Archive root manifest missing')
            require('.claude-plugin/marketplace.json' not in archive.namelist(), 'Marketplace leaked into plugin')
            extracted = Path(temp) / 'extracted'
            archive.extractall(extracted)
        state = Path(temp) / 'state'
        status = subprocess.run([sys.executable, str(extracted / 'scripts/runtime.py'), '--state', str(state), 'status'],
                                check=True, capture_output=True, text=True)
        data = json.loads(status.stdout)
        require(data['version'] == version and data['network'] == 'NOT_RUN', 'Extracted runtime status failed')
        require(len(data['providers']) == 14, 'Extracted provider registry differs')
    print('PASS: standalone source, all test suites, reproducible archive and isolated runtime status')


if __name__ == '__main__':
    main()
