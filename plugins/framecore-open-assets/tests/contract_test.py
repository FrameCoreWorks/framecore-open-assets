"""Task-contract envelope, discovery manifest and additive provenance; offline, no provider calls."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / 'scripts'))
import core
import runtime
import contract


def png():
    from PIL import Image
    data = io.BytesIO(); Image.new('RGB', (6, 4)).save(data, format='PNG')
    return data.getvalue()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Envelope(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.state = self.root / 'state'

    def tearDown(self):
        self.tmp.cleanup()

    def signed_results(self, rights='eligible'):
        item = core.asset('commons', 'File:x.png', 'X', 'Author', 'https://commons.wikimedia.org/wiki/File:x.png',
                          [core.variant('https://upload.wikimedia.org/x.png')], core.CC0, 'graphics')
        item['rights_status'] = rights
        payload = {'utc': core.utc(), 'fingerprint': runtime.fingerprint(), 'host': 'claude_code',
                   'query': 'x', 'category': 'graphics', 'items': [item], 'trace': []}
        path = self.root / 'results.json'
        path.write_text(json.dumps(runtime.seal(payload, self.state)))
        return path

    def run_cli(self, *argv):
        with patch.object(core.Client, 'get', return_value=(png(), {'content-type': 'image/png'})), \
                contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            code = runtime.main(['--state', str(self.state), *argv])
        return code, out.getvalue()

    def test_verify_writes_a_conforming_envelope_whose_hashes_match_the_files(self):
        results = self.signed_results()
        media, env = self.root / 'x.png', self.root / 'x.envelope.json'
        code, _ = self.run_cli('verify', '--host', 'claude_code', '--model', 'test-model', '--results', str(results),
                               '--out', str(media), '--envelope-out', str(env), '--task-id', 'task-1',
                               '--requester', 'framecore-work-creative-studio@1.151.0', '--owner', 'studio')
        self.assertEqual(code, 0)
        data = json.loads(env.read_text())
        self.assertEqual(contract.validate(data, 'result'), [])
        self.assertEqual((data['status'], data['task_id'], data['origin']), ('succeeded', 'task-1', 'studio'))
        files = {o['role']: o for o in data['outputs']}
        self.assertEqual(files['media']['sha256'], sha(media))
        self.assertEqual(files['sidecar']['sha256'], sha(str(media) + '.asset.json'))
        self.assertEqual(files['media']['hash_source'], 'local_only')
        self.assertEqual(data['inputs'][0]['sha256'], sha(results))
        self.assertEqual(data['asset']['licence']['rights_status'], 'eligible')
        self.assertTrue(any(c['check'].startswith('listening') for c in data['unexecuted_checks']))

    def test_sidecar_gains_additive_provenance_without_changing_existing_fields(self):
        results = self.signed_results()
        media = self.root / 'x.png'
        self.run_cli('verify', '--host', 'claude_code', '--model', 'test-model', '--results', str(results),
                     '--out', str(media), '--task-id', 'task-2')
        record = json.loads(Path(str(media) + '.asset.json').read_text())
        for key in ('provider', 'id', 'title', 'creator', 'source_page', 'license', 'license_url', 'attribution',
                    'selected_variant', 'saved_path', 'sha256', 'bytes', 'category', 'rights_status',
                    'technical_test_only', 'verification'):
            self.assertIn(key, record)
        self.assertEqual((record['host'], record['model'], record['runtime_version'], record['task_id']),
                         ('claude_code', 'test-model', core.VERSION, 'task-2'))
        self.assertEqual(record['fingerprint'], runtime.fingerprint())
        self.assertRegex(record['trace_sha256'], '^[0-9a-f]{64}$')
        self.assertEqual(record['hash_source'], 'local_only')
        self.assertIsNotNone(record['search_utc'])

    def test_standalone_envelope_has_no_task_id(self):
        results = self.signed_results()
        env = self.root / 'standalone.json'
        self.run_cli('verify', '--host', 'claude_code', '--model', 'm', '--results', str(results),
                     '--out', str(self.root / 's.png'), '--envelope-out', str(env))
        data = json.loads(env.read_text())
        self.assertEqual((data['task_id'], data['origin']), (None, 'standalone'))

    def test_rights_refusal_envelope_is_refused_and_keeps_the_error(self):
        results = self.signed_results(rights='blocked')
        env = self.root / 'refused.json'
        code, _ = self.run_cli('verify', '--host', 'claude_code', '--model', 'm', '--results', str(results),
                               '--out', str(self.root / 'r.png'), '--envelope-out', str(env))
        self.assertEqual(code, 2)
        data = json.loads(env.read_text())
        self.assertEqual(contract.validate(data, 'result'), [])
        self.assertEqual(data['status'], 'refused')
        self.assertEqual(data['errors'][0]['code'], 'rights_blocked')
        self.assertEqual(data['outputs'], [])

    def test_envelope_inside_package_is_refused_before_any_download(self):
        results = self.signed_results()
        with patch.object(core.Client, 'get') as network, contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            code = runtime.main(['--state', str(self.state), 'verify', '--host', 'claude_code', '--model', 'm',
                                 '--results', str(results), '--out', str(self.root / 'p.png'),
                                 '--envelope-out', str(PLUGIN / 'leak.json')])
        self.assertEqual(code, 2)
        network.assert_not_called()
        self.assertFalse((PLUGIN / 'leak.json').exists())
        self.assertFalse((self.root / 'p.png').exists())

    def test_technical_only_proof_does_not_unlock_production_download(self):
        results = self.signed_results(rights='review_sa')
        code, _ = self.run_cli('verify', '--host', 'claude_code', '--model', 'm', '--results', str(results),
                               '--out', str(self.root / 't.png'), '--technical-only')
        self.assertEqual(code, 0)
        self.assertFalse(runtime.proof_valid(self.state, 'claude_code', 'commons', 'graphics'))
        code, out = self.run_cli('download', '--host', 'claude_code', '--model', 'm', '--results', str(results),
                                 '--out', str(self.root / 'd.png'), '--accept-sa')
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(out)['error'], 'host_not_verified')

    def test_status_envelope_reports_readiness_without_network(self):
        env = self.root / 'status.json'
        with patch('urllib.request.build_opener') as network, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(runtime.main(['--state', str(self.root / 'absent'), 'status', '--envelope-out', str(env)]), 0)
        network.assert_not_called()
        data = json.loads(env.read_text())
        self.assertEqual(contract.validate(data, 'result'), [])
        self.assertIn(data['readiness']['state'], ('ready', 'unavailable'))


    def test_envelope_path_that_equals_a_command_output_is_refused_before_any_download(self):
        results = self.signed_results()
        media = self.root / 'c.png'
        for env in (media, Path(str(media) + '.asset.json'), results):
            with patch.object(core.Client, 'get') as network, contextlib.redirect_stdout(io.StringIO()) as out, \
                    contextlib.redirect_stderr(io.StringIO()):
                code = runtime.main(['--state', str(self.state), 'verify', '--host', 'claude_code', '--model', 'm',
                                     '--results', str(results), '--out', str(media), '--envelope-out', str(env)])
            self.assertEqual(code, 2, env)
            network.assert_not_called()
            self.assertEqual(json.loads(out.getvalue())['error'], 'output_exists', env)
            self.assertFalse(media.exists())

    def test_requester_needs_a_plugin_name_and_origin_needs_the_exact_studio_id(self):
        results = self.signed_results()
        code, out = self.run_cli('verify', '--host', 'claude_code', '--model', 'm', '--results', str(results),
                                 '--out', str(self.root / 'q.png'), '--requester', '@1')
        self.assertEqual((code, json.loads(out)['error']), (2, 'input_limit'))
        env = self.root / 'spoof.json'
        self.run_cli('verify', '--host', 'claude_code', '--model', 'm', '--results', str(results),
                     '--out', str(self.root / 'q2.png'), '--envelope-out', str(env), '--task-id', 't',
                     '--requester', 'framecore-work-creative-studio-fake@1')
        self.assertEqual(json.loads(env.read_text())['origin'], 'other')

    def test_search_envelope_lists_the_signed_results_file(self):
        out, env = self.root / 'search.json', self.root / 'search.envelope.json'
        item = core.asset('commons', 'File:x.png', 'X', 'A', 'https://commons.wikimedia.org/wiki/File:x.png',
                          [core.variant('https://upload.wikimedia.org/x.png')], core.CC0, 'graphics')
        with patch.object(runtime, 'search_one', return_value=[item]), contextlib.redirect_stdout(io.StringIO()):
            code = runtime.main(['--state', str(self.state), 'search', '--host', 'claude_code', '--model', 'm',
                                 '--provider', 'commons', '--category', 'graphics', '--query', 'x', '--out', str(out),
                                 '--envelope-out', str(env)])
        self.assertEqual(code, 0)
        data = json.loads(env.read_text())
        self.assertEqual(contract.validate(data, 'result'), [])
        self.assertEqual(data['outputs'][0]['sha256'], sha(out))

    def test_failure_after_files_were_saved_reports_them_as_partial(self):
        results = self.signed_results()
        media, env = self.root / 'f.png', self.root / 'f.envelope.json'
        with patch.object(runtime.os, 'replace', side_effect=OSError('disk full')):
            code, _ = self.run_cli('verify', '--host', 'claude_code', '--model', 'm', '--results', str(results),
                                   '--out', str(media), '--envelope-out', str(env))
        self.assertEqual(code, 2)
        data = json.loads(env.read_text())
        self.assertEqual(contract.validate(data, 'result'), [])
        self.assertEqual(data['status'], 'partial')
        self.assertEqual({o['role'] for o in data['outputs']}, {'media', 'sidecar'})

    def test_envelope_write_failure_is_a_clean_failure_not_a_traceback(self):
        env = self.root / 'locked.json'
        with patch.object(runtime, 'save_new', side_effect=OSError('permission denied')), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
            code = runtime.main(['--state', str(self.root / 'absent'), 'status', '--envelope-out', str(env)])
        self.assertEqual(code, 2)
        self.assertIn('Envelope not written', err.getvalue())

    def test_deliberate_gates_map_to_refused(self):
        for kind in ('size_limit', 'provider_mismatch', 'rights_blocked'):
            self.assertEqual(contract.status_for(kind), 'refused')

class Contract(unittest.TestCase):
    def test_validator_rejects_malformed_results(self):
        good = {'contract': 'framecore-task-result/1', 'task_id': None, 'origin': 'standalone',
                'provider': {'plugin': 'framecore-open-assets', 'capability': 'open-assets', 'operation': 'status'},
                'status': 'succeeded', 'host': None, 'inputs': [], 'outputs': [], 'readiness': {'state': 'ready'},
                'commands_run': [], 'verification_evidence': [], 'warnings': [], 'errors': [], 'unexecuted_checks': []}
        self.assertEqual(contract.validate(good, 'result'), [])
        for change in ({'contract': 'framecore-task-result/2'}, {'status': 'PASS'}, {'origin': 'cloud'},
                       {'outputs': [{'path': 'x', 'sha256': 'abc', 'bytes': 1}]},
                       {'outputs': [{'path': 'x', 'sha256': '0' * 64}]}, {'readiness': {'state': 'maybe'}}):
            self.assertNotEqual(contract.validate({**good, **change}, 'result'), [], change)
        missing = dict(good); missing.pop('task_id')
        self.assertNotEqual(contract.validate(missing, 'result'), [])

    def test_capabilities_manifest_matches_package_and_schema(self):
        caps = json.loads((PLUGIN / 'capabilities.json').read_text())
        self.assertEqual(contract.validate(caps, 'capabilities'), [])
        manifest = json.loads((PLUGIN / 'plugin.json').read_text())
        self.assertEqual((caps['plugin']['name'], caps['plugin']['version']), (manifest['name'], manifest['version']))
        self.assertEqual(caps['contract_schema']['sha256'], sha(PLUGIN / caps['contract_schema']['path']))
        self.assertTrue((PLUGIN / caps['entry_skill']).is_file())
        cap = caps['capabilities'][0]
        parser_source = (PLUGIN / 'scripts/runtime.py').read_text()
        self.assertEqual(cap['operations'], ['status', 'domains', 'reach', 'search', 'verify', 'download'])
        for flag in cap['envelope_flags']:
            self.assertIn(f"'{flag}'", parser_source)
        categories = sorted({c for row in core.REGISTRY.values() for c in row['categories']})
        self.assertEqual(sorted(cap['categories']), categories)

    def test_every_refusal_code_is_documented(self):
        codes = set()
        for path in (PLUGIN / 'scripts').rglob('*.py'):
            codes |= set(re.findall(r"Refused\('([a-z_]+)'", path.read_text()))
        codes |= {'access_denied', 'rate_limited', 'server_error', 'http_error', 'invalid_input_or_response'}
        documented = (PLUGIN / 'skills/open-assets/references/contract.md').read_text()
        self.assertEqual(sorted(c for c in codes if f'`{c}`' not in documented), [])

    def test_package_names_this_repository_not_the_studio_monorepo(self):
        for path in PLUGIN.rglob('*'):
            if path.is_file() and path.suffix in ('.py', '.json', '.md', '.yaml') and 'tests' not in path.parts:
                self.assertNotIn('framecore-works-creative-studio', path.read_text(), path)


if __name__ == '__main__':
    unittest.main()
