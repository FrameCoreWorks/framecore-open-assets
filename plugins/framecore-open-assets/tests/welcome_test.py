"""The bare-invocation welcome in SKILL.md is a byte-exact copy of the English asset."""
import re
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / 'skills' / 'open-assets'


class WelcomeTest(unittest.TestCase):
    def test_embedded_welcome_matches_asset(self):
        text = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
        found = re.findall(r'<!-- welcome:start -->\n(.*?)\n<!-- welcome:end -->', text, re.S)
        self.assertEqual(len(found), 1)
        asset = (SKILL / 'assets' / 'startup-welcome.en.md').read_text(encoding='utf-8')
        self.assertEqual(found[0] + '\n', asset)

    def test_welcome_shape(self):
        asset = (SKILL / 'assets' / 'startup-welcome.en.md').read_text(encoding='utf-8')
        self.assertTrue(asset.startswith('I am '))
        self.assertTrue(asset.rstrip().endswith('?'))
        self.assertGreaterEqual(len(re.findall(r'^- \*\*', asset, re.M)), 4)
        self.assertGreaterEqual(len(re.findall(r'^- "', asset, re.M)), 3)
        self.assertNotIn('Creative Studio', asset)

    def test_rule_points_to_welcome(self):
        text = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
        for phrase in ('## Welcome', 'A bare invocation is', 'copy it exactly', 'translate all of it',
                       '](assets/startup-welcome.en.md)'):
            self.assertIn(phrase, text)


if __name__ == '__main__':
    unittest.main()
