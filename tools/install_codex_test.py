"""Offline tests for the Codex native-entry installer."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import install_codex
from package import PLUGIN


class InstallCodex(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name).resolve()
        self.plugin = self.base / 'repo/plugins/framecore-open-assets'
        shutil.copytree(PLUGIN, self.plugin, ignore=shutil.ignore_patterns('__pycache__'))
        self.commit = 'a' * 40

    def tearDown(self):
        self.temp.cleanup()

    def run_install(self, action, bundle=None):
        return install_codex.run(action, self.plugin, self.base / 'skills',
                                 bundle or self.base / 'bundle', self.commit)

    def test_plan_install_repeat_and_verify(self):
        self.assertEqual(self.run_install('plan')['status'], 'READY')
        self.assertFalse((self.base / 'skills').exists())
        self.assertEqual(self.run_install('install')['status'], 'FILES_VERIFIED')
        entry = self.base / 'skills/open-assets/SKILL.md'
        text = entry.read_text()
        self.assertTrue(text.startswith('---\nname: open-assets\n'))
        self.assertIn(str(self.base / 'bundle/skills/open-assets/SKILL.md'), text)
        self.assertIn('runtime.py status --host codex', text)
        self.assertTrue((self.base / 'bundle/scripts/runtime.py').is_file())
        receipt = json.loads((self.base / 'skills/open-assets/installation.json').read_text())
        self.assertEqual(receipt['source_commit'], self.commit)
        before = entry.stat().st_mtime_ns
        self.assertEqual(self.run_install('install')['status'], 'already_up_to_date')
        self.assertEqual(entry.stat().st_mtime_ns, before)
        self.assertEqual(self.run_install('verify')['host_activation'], 'NOT_RUN')

    def test_runtime_cache_does_not_break_verify(self):
        self.run_install('install')
        cache = self.base / 'bundle/scripts/__pycache__'
        cache.mkdir()
        (cache / 'core.cpython-312.pyc').write_bytes(b'cache')
        self.assertEqual(self.run_install('verify')['status'], 'FILES_VERIFIED')

    def test_edited_bundle_is_preserved_and_rejected(self):
        self.run_install('install')
        skill = self.base / 'bundle/skills/open-assets/SKILL.md'
        skill.write_text('user changes')
        with self.assertRaises(ValueError):
            self.run_install('install')
        self.assertEqual(skill.read_text(), 'user changes')
        with self.assertRaises(ValueError):
            self.run_install('verify')

    def test_partial_overlapping_and_bad_inputs_are_rejected(self):
        (self.base / 'bundle').mkdir()
        with self.assertRaises(ValueError):
            self.run_install('install')
        with self.assertRaises(ValueError):
            self.run_install('install', self.base / 'skills/bundle')
        with self.assertRaises(ValueError):
            install_codex.run('install', self.plugin, self.base / 'skills', self.base / 'b2', 'main')
        with self.assertRaises(ValueError):
            install_codex.run('install', self.plugin, Path('relative'), self.base / 'b3', self.commit)


if __name__ == '__main__':
    unittest.main()
