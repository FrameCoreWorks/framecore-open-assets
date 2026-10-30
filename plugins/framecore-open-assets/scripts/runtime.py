#!/usr/bin/env python3
"""FrameCore Open Assets CLI. Local execution; public read-only provider APIs."""
import argparse
import hashlib
import hmac
import importlib
import json
import os
from pathlib import Path
import shutil
import socket
import sys
import tempfile
import urllib.parse
import urllib.request

from core import ROOT, REGISTRY, VERSION, Refused, Client, download, utc
import contract

HOSTS = ('chatgpt_work', 'claude_code', 'claude_apps', 'codex')
WORKAROUNDS = ('Do not retry. Tell the user in one or two sentences that this environment blocks the provider, then offer: '
               'allow the hosts printed by `runtime.py domains` in the host\'s network settings; run the task on a '
               'computer with open internet; or continue with the user\'s own files or assets made in code.')


def fingerprint():
    digest = hashlib.sha256()
    paths = [ROOT / 'providers.json', *sorted((ROOT / 'scripts').rglob('*.py'))]
    for p in paths:
        digest.update(p.relative_to(ROOT).as_posix().encode()); digest.update(p.read_bytes())
    return digest.hexdigest()


def state_key(state):
    path = Path(state) / 'result-signing.key'
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            with os.fdopen(fd, 'wb') as f:
                f.write(os.urandom(32))
        except FileExistsError:
            pass
    return path.read_bytes()


def seal(payload, state):
    raw = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    return {'payload': payload, 'signature': hmac.new(state_key(state), raw, hashlib.sha256).hexdigest()}


def unseal(bundle, state):
    payload = bundle['payload']
    if not (Path(state) / 'result-signing.key').is_file():
        raise Refused('untrusted_result', 'No local provenance key; run a fresh search')
    expected = seal(payload, state)['signature']
    if not hmac.compare_digest(expected, bundle.get('signature', '')) or payload.get('fingerprint') != fingerprint():
        raise Refused('untrusted_result', 'Search result was changed, came from another state directory, or predates this runtime')
    from datetime import datetime, timezone
    age = (datetime.now(timezone.utc) - datetime.fromisoformat(payload['utc'])).total_seconds()
    if not 0 <= age <= 86400:
        raise Refused('stale_result', 'Search again; this result is older than one day')
    return payload


def save_new(path, obj):
    path = Path(path)
    if ROOT == path.resolve() or ROOT in path.resolve().parents:
        raise Refused('package_output', 'Write operational output outside the plugin package')
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open('x') as f:
            json.dump(obj, f, indent=2); f.write('\n')
    except FileExistsError:
        raise Refused('output_exists', 'Output already exists: ' + str(path))


def allowlist(providers=None):
    """Every reviewed provider host once, in registry order; a leading-dot suffix becomes `*.`."""
    out = []
    for name, row in REGISTRY.items():
        if providers and name not in providers:
            continue
        for domain in row['allowed_domains']:
            domain = '*' + domain if domain.startswith('.') else domain
            if domain not in out:
                out.append(domain)
    return out


def proxy_for(host):
    proxy = urllib.request.getproxies().get('https')
    return None if not proxy or urllib.request.proxy_bypass(host) else proxy


def probe(host, proxy, timeout=6):
    """Open a connection to host:443 (through the host's proxy when set) and close it; no HTTP request."""
    try:
        if proxy:
            p = urllib.parse.urlsplit(proxy)
            with socket.create_connection((p.hostname, p.port or 80), timeout=timeout) as conn:
                conn.sendall(f'CONNECT {host}:443 HTTP/1.1\r\nHost: {host}:443\r\n\r\n'.encode())
                line = conn.recv(256).split(b'\r\n', 1)[0].decode('latin-1').split()
            code = line[1] if len(line) > 1 else ''
            return 'reachable' if code == '200' else 'blocked' if code in ('403', '407') else 'unknown'
        with socket.create_connection((host, 443), timeout=timeout):
            return 'reachable'
    except socket.gaierror:
        return 'no_dns'
    except OSError:
        return 'unreachable'


def reach(providers):
    rows, seen = {}, {}
    for name in providers:
        domains = {}
        for domain in REGISTRY[name]['allowed_domains']:
            if domain.startswith('.'):
                domains['*' + domain] = 'not_probed'
                continue
            if domain not in seen:
                print(json.dumps({'next_probe': domain, 'hypothesis': 'Can this environment open a connection to '
                                  + domain + '? Connection only; no HTTP request'}), file=sys.stderr, flush=True)
                seen[domain] = probe(domain, proxy_for(domain))
            domains[domain] = seen[domain]
        states = {v for v in domains.values() if v != 'not_probed'}
        state = ('reachable' if states == {'reachable'} else 'blocked' if 'blocked' in states
                 else 'unreachable' if states & {'unreachable', 'no_dns'} else 'unknown')
        rows[name] = {'state': state, 'domains': domains}
    ready = [n for n, r in rows.items() if r['state'] == 'reachable']
    output = {'version': VERSION, 'network': 'open' if len(ready) == len(rows) else 'blocked' if not ready
              else 'partly_blocked', 'probe': 'connection to port 443 only; providers receive no HTTP request',
              'providers': rows, 'ready_providers': ready,
              'blocked_domains': [d for d, s in seen.items() if s != 'reachable'], 'allowlist': allowlist()}
    if output['network'] != 'open':
        output['advice'] = WORKAROUNDS
    return output


def search_one(client, query, category, limit):
    module = client.policy['module']
    if category not in client.policy['categories']:
        raise Refused('unsupported_category', 'This provider does not implement that category')
    results = importlib.import_module('providers.' + module).search(client, query, category, limit)
    for r in results:
        for v in r['variants']:
            from core import validate_url
            validate_url(v['url'], client.policy['allowed_domains'])
    return results


def proof_path(state, host, provider, category):
    return Path(state) / f'verified-{host}-{provider}-{category}.json'


def proof_valid(state, host, provider, category):
    path = proof_path(state, host, provider, category)
    if not path.exists():
        return False
    try:
        proof = unseal(json.loads(path.read_text()), state)
        # A technical-only proof tests transport and decoding; it never clears production downloads.
        return (proof.get('status') == 'PASS' and proof.get('host') == host and proof.get('provider') == provider
                and proof.get('category') == category and not proof.get('technical_test_only', False))
    except (Refused, ValueError, KeyError, TypeError, OSError):
        return False


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_new_output(path):
    path = Path(path)
    if ROOT == path.resolve() or ROOT in path.resolve().parents:
        raise Refused('package_output', 'Write operational output outside the plugin package')
    if path.exists() or path.is_symlink():
        raise Refused('output_exists', 'Output already exists: ' + str(path))


def requester(text):
    if not text:
        return None
    plugin, _, version = text.partition('@')
    if not plugin.strip():
        raise Refused('input_limit', 'Give the requester as name@version, for example framecore-work-creative-studio@1.151.0')
    return {'plugin': plugin, 'version': version or None}


def output_records(output):
    media = Path(output['saved_path']); sidecar = Path(str(media) + '.asset.json')
    hash_source = output.get('hash_source', 'local_only')
    return [contract.file_record(media, output['sha256'], output['bytes'], media_kind=output['verification'].get('kind'),
                                 role='media', derived_from=[], sidecar=str(sidecar), hash_source=hash_source),
            contract.file_record(sidecar, sha256_file(sidecar), sidecar.stat().st_size, media_kind='source_record',
                                 role='sidecar', derived_from=[output['sha256']], sidecar=None, hash_source='local_only')]


def envelope(args, argv, code, output, error=None):
    """Describe one CLI run as a framecore-task-result/1 document; stdout stays unchanged."""
    command = args.command
    who = requester(args.requester)
    origin = 'standalone' if not args.task_id else (
        'studio' if who and who['plugin'] == 'framecore-work-creative-studio' else 'other')
    result = {'contract': contract.RESULT, 'task_id': args.task_id, 'origin': origin,
              'requester': who, 'owner': args.owner,
              'provider': {'plugin': 'framecore-open-assets', 'version': VERSION, 'capability': 'open-assets',
                           'operation': command, 'command': None},
              'status': 'succeeded', 'host': getattr(args, 'host', None), 'model': getattr(args, 'model', None),
              'inputs': [], 'outputs': [], 'readiness': {'state': 'ready', 'command': 'runtime.py status', 'observed_at': utc(),
                                                         'details': None},
              'commands_run': [{'argv': ['runtime.py', *argv], 'exit_code': code, 'started': None, 'duration_s': None}],
              'verification_evidence': [], 'warnings': [], 'errors': [], 'unexecuted_checks': [], 'asset': None}
    if command in ('verify', 'download') and Path(args.results).is_file():
        result['inputs'].append({'path': str(Path(args.results).resolve()), 'sha256': sha256_file(args.results),
                                 'bytes': Path(args.results).stat().st_size, 'role': 'signed_search_results', 'provenance': None})
    if error is not None:
        result['status'] = contract.status_for(error['error'])
        result['errors'].append({'code': error['error'], 'message': error['message'], 'next_action': error['next_action']})
        if error['error'] == 'decoder_missing':
            result['readiness']['state'] = 'unavailable'
        if output and command in ('verify', 'download'):
            # Files were saved before a later step failed: report them instead of hiding them.
            result['status'] = 'partial'
            result['outputs'] += output_records(output)
        return result
    if command == 'status':
        result['readiness'] = {'state': 'ready' if output['python_ready'] else 'unavailable', 'command': 'runtime.py status',
                               'observed_at': utc(), 'details': {k: output[k] for k in ('python', 'pillow', 'ffprobe', 'ffmpeg')}}
        if not (output['pillow'] and output['ffprobe'] and output['ffmpeg']):
            result['warnings'].append('Some decoders are missing; affected media categories will be blocked')
        result['unexecuted_checks'].append({'check': 'provider network', 'reason': 'status never contacts providers'})
    elif command == 'search':
        out = Path(args.out).resolve()
        result['outputs'].append(contract.file_record(out, sha256_file(out), out.stat().st_size, media_kind='search_results',
                                                      role='signed_search_results', derived_from=[], sidecar=None, hash_source='local_only'))
        result['verification_evidence'].append({'check': 'result signed with the local provenance key', 'result': 'pass',
                                                'scope': 'search file', 'detail': None})
        result['unexecuted_checks'] += [{'check': 'download and decode', 'reason': 'search only lists candidates'},
                                        {'check': 'rights review of each candidate', 'reason': 'done by the person before download'}]
    else:
        hash_source = output.get('hash_source', 'local_only')
        result['outputs'] += output_records(output)
        result['asset'] = {'provider': output['provider'], 'asset_id': output['id'], 'source_url': output['source_page'],
                           'selected_variant': output['selected_variant'],
                           'licence': {'name': output['license'], 'url': output['license_url'],
                                       'rights_status': output['rights_status'],
                                       'share_alike_accepted': output['share_alike_accepted'],
                                       'rights_review_note': output['rights_review_note'],
                                       'technical_test_only': output['technical_test_only']},
                           'attribution': output['attribution'], 'credits': {'creator': output['creator']},
                           'retrieval': {'search_utc': output.get('search_utc'), 'retrieved_utc': output.get('retrieved_utc'),
                                         'downloaded_utc': output['downloaded_utc']}}
        result['verification_evidence'] += [
            {'check': 'full local decode', 'result': 'pass', 'scope': 'downloaded file', 'detail': output['verification']},
            {'check': 'provider SHA-256', 'result': 'pass' if hash_source == 'provider' else 'not_run',
             'scope': 'downloaded file', 'detail': None},
            {'check': 'provider byte count', 'result': 'pass' if output['selected_variant'].get('bytes') else 'not_run',
             'scope': 'downloaded file', 'detail': None}]
        result['warnings'] += output.get('warnings', [])
        if output['technical_test_only']:
            result['warnings'].append('Technical test only: excluded from production reuse')
        result['unexecuted_checks'] += [
            {'check': 'listening or visual suitability review', 'reason': 'a decoded file is not a quality review'},
            {'check': 'reading the licence page for this use', 'reason': 'rights status comes from provider metadata'}]
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', default=os.environ.get('FRAMECORE_OPEN_ASSETS_STATE',
                        str(Path.home() / '.framecore-open-assets')))
    sub = parser.add_subparsers(dest='command', required=True)
    status = sub.add_parser('status', help='Read local capabilities and provider policy; no network')
    status.add_argument('--host', choices=HOSTS, help='Report readiness only for this actual executing host')
    for name in ('search', 'verify', 'download'):
        p = sub.add_parser(name)
        p.add_argument('--host', choices=HOSTS, required=True, help='Actual executing host; never substitute another host label')
        p.add_argument('--model', required=True, help='Actual agent model identifier for honest User-Agent')
        p.add_argument('--out', required=True)
        if name == 'search':
            p.add_argument('--provider', choices=[*REGISTRY, 'all'], required=True)
            p.add_argument('--category', choices=['photos', 'graphics', 'audio', 'music', 'sfx', 'video'], required=True)
            p.add_argument('--query', required=True)
            p.add_argument('--limit', type=int, default=3)
            p.add_argument('--fresh', action='store_true')
        else:
            p.add_argument('--results', required=True)
            p.add_argument('--index', type=int, default=0)
            p.add_argument('--variant', type=int, default=0)
            p.add_argument('--accept-sa', action='store_true')
            p.add_argument('--rights-review-note', help='Item-specific review evidence, intended use and jurisdiction, supplied by the user')
            if name == 'verify':
                p.add_argument('--technical-only', action='store_true',
                               help='Test transport/decoder only; media remains excluded from production reuse')
    for p in sub.choices.values():
        p.add_argument('--envelope-out', help='Also write a framecore-task-result/1 envelope to this new file')
        p.add_argument('--task-id', help='Caller task id to echo; omit for a standalone job')
        p.add_argument('--requester', help='Calling plugin as name@version, e.g. framecore-work-creative-studio@1.151.0')
        p.add_argument('--owner', help='Who accepts the result (for example studio or user)')
    domains = sub.add_parser('domains', help='Print every reviewed provider host, one per line, for a network allowlist; no network')
    domains.add_argument('--provider', choices=list(REGISTRY), action='append')
    probe_cmd = sub.add_parser('reach', help='Check which providers this environment can connect to; no HTTP request')
    probe_cmd.add_argument('--provider', choices=list(REGISTRY), action='append')
    for p in (domains, probe_cmd):
        p.set_defaults(envelope_out=None, task_id=None, requester=None, owner=None)
    argv = list(sys.argv[1:] if argv is None else argv)
    args = parser.parse_args(argv)
    if args.command == 'domains':
        print('\n'.join(allowlist(args.provider)))
        return 0
    if args.command == 'reach':
        print(json.dumps(reach(args.provider or list(REGISTRY)), indent=2))
        return 0
    clients = []
    output = error = None
    envelope_ok = False
    try:
        requester(args.requester)
        if args.envelope_out:
            check_new_output(args.envelope_out)
            own = {Path(p).resolve() for p in (getattr(args, 'out', None), getattr(args, 'results', None)) if p}
            if getattr(args, 'out', None):
                own.add(Path(str(args.out) + '.asset.json').resolve())
            if Path(args.envelope_out).resolve() in own:
                raise Refused('output_exists', 'The envelope needs its own path, not the command output, sidecar or results file')
            envelope_ok = True
        if args.command == 'status':
            import importlib.util
            output = {'version': VERSION, 'fingerprint': fingerprint(), 'python': sys.version.split()[0],
                      'python_ready': sys.version_info >= (3, 10),
                      'pillow': importlib.util.find_spec('PIL') is not None,
                      'ffprobe': bool(shutil.which('ffprobe')), 'ffmpeg': bool(shutil.which('ffmpeg')),
                      'network': 'NOT_RUN', 'providers': REGISTRY,
                      'host_results': {h: {p: {c: 'PASS' if proof_valid(args.state, h, p, c) else 'NOT_RUN'
                                                for c in row['categories']} for p, row in REGISTRY.items()}
                                       for h in ((args.host,) if args.host else HOSTS)}}
            if args.host:
                output['host'] = args.host
        elif args.command == 'search':
            if not 1 <= args.limit <= 5 or not 1 <= len(args.query.strip()) <= 240:
                raise Refused('input_limit', 'Use 1-5 results and a query of 1-240 characters')
            if Path(args.out).exists():
                raise Refused('output_exists', 'Choose a new result file before making network calls')
            selected = [args.provider] if args.provider != 'all' else [p for p, row in REGISTRY.items()
                        if row['policy'] == 'documented' and args.category in row['categories']]
            items = []
            for provider in selected:
                client = Client(provider, args.state, args.host, args.model, args.fresh)
                clients.append(client)
                items.extend(search_one(client, args.query, args.category, args.limit))
            payload = {'utc': utc(), 'fingerprint': fingerprint(), 'host': args.host,
                       'query': args.query, 'category': args.category, 'items': items,
                       'trace': [event for c in clients for event in c.trace]}
            output = seal(payload, args.state)
            save_new(args.out, output)
        else:
            if Path(args.results).stat().st_size > 8 * 1024 * 1024:
                raise Refused('result_size', 'Result JSON exceeds 8 MiB')
            payload = unseal(json.loads(Path(args.results).read_text()), args.state)
            if payload['host'] != args.host:
                raise Refused('host_mismatch', 'Run a fresh search in the actual target host')
            if args.index < 0 or args.variant < 0:
                raise Refused('invalid_index', 'Indices start at zero')
            item = payload['items'][args.index]
            provider, category = item['provider'], item['category']
            if args.command == 'download' and not proof_valid(args.state, args.host, provider, category):
                raise Refused('host_not_verified', 'Use verify for the first selected asset on this host/category')
            client = Client(provider, args.state, args.host, args.model, fresh=True); clients.append(client)
            output = None
            output = download(client, item, args.out, args.variant, args.accept_sa, args.rights_review_note,
                              technical_only=getattr(args, 'technical_only', False),
                              provenance={'fingerprint': fingerprint(), 'search_utc': payload['utc'],
                                          'search_query': payload.get('query'), 'task_id': args.task_id})
            output['trace'] = client.trace
            if args.command == 'verify':
                proof = {'utc': utc(), 'fingerprint': fingerprint(), 'host': args.host, 'provider': provider,
                         'category': category, 'status': 'PASS', 'sha256': output['sha256'],
                         'rights_status': item['rights_status'], 'technical_test_only': output['technical_test_only'], 'scope': 'One actual search-to-decoded-file path; not universal rights clearance'}
                path = proof_path(args.state, args.host, provider, category)
                # Replace only this command's readiness record, never user media or result files.
                with tempfile.NamedTemporaryFile('w', dir=path.parent, delete=False) as f:
                    json.dump(seal(proof, args.state), f); temp = f.name
                os.replace(temp, path)
        print(json.dumps(output, indent=2))
        code = 0
    except Exception as exc:
        # This is the CLI boundary: malformed provider shapes, decoder failures and corrupt
        # archives must produce a failed result, never a traceback that looks like success.
        error = {'status': 'FAIL', 'error': getattr(exc, 'kind', 'invalid_input_or_response'),
                 'message': str(exc), 'trace': [e for c in clients for e in c.trace],
                 'next_action': WORKAROUNDS if getattr(exc, 'kind', '') == 'network_blocked'
                 else 'Report this failure and ask before switching provider or route.'}
        print(json.dumps(error, indent=2))
        code = 2
    if args.envelope_out and envelope_ok:
        try:
            document = envelope(args, argv, code, output, error)
            problems = contract.validate(document, 'result')
            if problems:
                raise Refused('invalid_envelope', '; '.join(problems))
            save_new(args.envelope_out, document)
        except Exception as exc:
            print(json.dumps({'status': 'FAIL', 'error': getattr(exc, 'kind', 'envelope_write_failed'),
                              'message': 'Envelope not written: ' + str(exc)}), file=sys.stderr)
            return 2
    return code


if __name__ == '__main__':
    raise SystemExit(main())
