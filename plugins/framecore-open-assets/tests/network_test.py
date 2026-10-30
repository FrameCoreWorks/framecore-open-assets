"""Blocked-network detection: proxy denials, the allowlist and the reach probe. No provider calls."""
import contextlib
import io
import json
from pathlib import Path
import socket
import sys
import tempfile
import threading
import unittest
import urllib.error
from unittest.mock import patch

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / 'scripts'))
import core
import runtime


def expected_allowlist():
    out = []
    for row in core.REGISTRY.values():
        for d in row['allowed_domains']:
            d = '*' + d if d.startswith('.') else d
            if d not in out:
                out.append(d)
    return out


class FakeProxy:
    """A local HTTP proxy that answers CONNECT with a fixed status per target host."""
    def __init__(self, answers):
        self.answers, self.seen = answers, []
        self.server = socket.socket()
        self.server.bind(('127.0.0.1', 0))
        self.server.listen(8)
        self.url = 'http://127.0.0.1:%d' % self.server.getsockname()[1]
        self.thread = threading.Thread(target=self.serve, daemon=True)
        self.thread.start()

    def serve(self):
        while True:
            try:
                conn, _ = self.server.accept()
            except OSError:
                return
            with conn:
                data = conn.recv(4096).decode()
                line = data.split('\r\n', 1)[0]
                self.seen.append(line)
                host = line.split()[1].rsplit(':', 1)[0]
                code = self.answers.get(host, 200)
                conn.sendall(('HTTP/1.1 %d X\r\n\r\n' % code).encode())

    def close(self):
        self.server.close()


class Network(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *argv):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = runtime.main(['--state', str(self.root / 'state'), *argv])
        return code, output.getvalue()

    def test_proxy_denial_is_reported_as_network_blocked(self):
        client = core.Client('commons', self.root / 'state', 'claude_code', 'test-model')
        denial = urllib.error.URLError(OSError('Tunnel connection failed: 403 Forbidden'))
        with patch('urllib.request.build_opener') as opener, patch('time.sleep'):
            opener.return_value.open.side_effect = denial
            with self.assertRaises(core.Refused) as raised:
                client.get('https://commons.wikimedia.org/w/api.php?action=query', 'blocked test')
        self.assertEqual(raised.exception.kind, 'network_blocked')
        self.assertIn('commons.wikimedia.org', str(raised.exception))
        self.assertIn('runtime.py domains', str(raised.exception))

    def test_other_transport_errors_stay_transport_errors(self):
        client = core.Client('commons', self.root / 'state', 'claude_code', 'test-model')
        with patch('urllib.request.build_opener') as opener, patch('time.sleep'):
            opener.return_value.open.side_effect = urllib.error.URLError(OSError('timed out'))
            with self.assertRaises(core.Refused) as raised:
                client.get('https://commons.wikimedia.org/w/api.php?action=query', 'timeout test')
        self.assertEqual(raised.exception.kind, 'transport_error')

    def test_search_failure_tells_agent_how_to_work_around_a_block(self):
        denial = core.Refused('network_blocked', 'blocked')
        with patch.object(core.Client, 'json', side_effect=denial):
            code, out = self.run_cli('search', '--provider', 'met', '--category', 'graphics', '--query', 'sun',
                                     '--host', 'claude_code', '--model', 'test', '--out', str(self.root / 'r.json'))
        result = json.loads(out)
        self.assertEqual((code, result['error']), (2, 'network_blocked'))
        self.assertIn('runtime.py domains', result['next_action'])
        self.assertIn('own files', result['next_action'])

    def test_domains_prints_every_allowed_domain_once_without_network(self):
        with patch('urllib.request.build_opener') as network, patch('socket.create_connection') as sock:
            code, out = self.run_cli('domains')
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines(), expected_allowlist())
        self.assertIn('*.archive.org', out.splitlines())
        network.assert_not_called(); sock.assert_not_called()
        self.assertFalse((self.root / 'state').exists())

    def test_probe_through_proxy_sends_only_connect(self):
        proxy = FakeProxy({'blocked.example': 403})
        try:
            self.assertEqual(runtime.probe('open.example', proxy.url), 'reachable')
            self.assertEqual(runtime.probe('blocked.example', proxy.url), 'blocked')
        finally:
            proxy.close()
        self.assertEqual(proxy.seen, ['CONNECT open.example:443 HTTP/1.1', 'CONNECT blocked.example:443 HTTP/1.1'])

    def test_reach_reports_blocked_providers_and_the_allowlist(self):
        def fake(host, proxy):
            return 'blocked' if host.endswith('wikimedia.org') else 'reachable'
        with patch.object(runtime, 'probe', side_effect=fake) as probed, \
                patch('urllib.request.build_opener') as network:
            code, out = self.run_cli('reach', '--provider', 'commons', '--provider', 'met')
        result = json.loads(out)
        self.assertEqual(code, 0)
        network.assert_not_called()
        self.assertEqual(result['network'], 'partly_blocked')
        self.assertEqual(result['providers']['commons']['state'], 'blocked')
        self.assertEqual(result['providers']['met']['state'], 'reachable')
        self.assertEqual(result['ready_providers'], ['met'])
        self.assertIn('upload.wikimedia.org', result['blocked_domains'])
        self.assertEqual(result['allowlist'], expected_allowlist())
        self.assertTrue(result['advice'])
        self.assertNotIn('.archive.org', [c.args[0] for c in probed.call_args_list])

    def test_reach_skips_wildcards_and_reports_open_network(self):
        with patch.object(runtime, 'probe', return_value='reachable') as probed:
            code, out = self.run_cli('reach', '--provider', 'librivox')
        result = json.loads(out)
        self.assertEqual((code, result['network']), (0, 'open'))
        self.assertEqual(result['providers']['librivox']['domains']['*.archive.org'], 'not_probed')
        self.assertEqual(sorted(c.args[0] for c in probed.call_args_list), ['archive.org', 'librivox.org'])
        self.assertNotIn('advice', result)


if __name__ == '__main__':
    unittest.main()
