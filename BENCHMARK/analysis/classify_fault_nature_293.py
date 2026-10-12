#!/usr/bin/env python3
"""Classify the 293 not-reproduced active bugs by their FAULT NATURE, inferred from each
issue's body/title (there is no runtime evidence, so we only infer what is determinable;
uncertain bugs are left with an empty category).

This is a fault-nature taxonomy (concurrency, serialisation, protocol, error handling,
discovery, transport/config, auth, environment/packaging, example, external-dependency),
NOT the exposure channel and NOT the Taraghi taxonomy (which we deliberately do not use).

Only categories that can be reliably inferred from the issue description are assigned;
anything ambiguous stays 'unknown'.

Outputs:
  - data/full_pool/fault_nature_293.json  (per-bug number, origin, nature, title, body_head)
  - docs/FAULT_NATURE_293.md              (distribution + per-bug table + prose)

Run from MCP-Fault-Benchmark/:
    python analysis/classify_fault_nature_293.py
"""
import os, json, re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..'))
FP = os.path.join(REPO, 'data', 'full_pool')
DOCS = os.path.join(REPO, 'docs')
os.makedirs(DOCS, exist_ok=True)

CONF = os.path.join(FP, 'confirmed_bugs.json')
FIXED = os.path.join(FP, 'fixed_removed.json')
AN = os.path.join(FP, 'active_dataset_analysis.json')
LABELS = os.path.join(FP, 'origin_labels.json')

# ordered rules: first matching rule wins. Each rule = (nature, [strong signal phrases])
# Classification uses the TITLE (cleanest, most explicit signal) first; only if the title
# gives no clear signal do we look at the body. Keywords are STRONG / specific phrases,
# not ubiquitous words (e.g. we use 'cannot connect' not 'connect', 'hang forever' not 'hang').
TITLE_RULES = [
    ('auth/credentials',
     ['oauth', 'auth token', 'api key', 'apikey', 'credential', '401', '403', 'authentication',
      'unauthorized', 'forbidden', 'permission denied', 'auth provider', 'bearer', 'token']),
    ('transport/connection',
     ['sse', 'streamable', 'stdio', 'transport', 'connect', 'redirect', 'endpoint', 'port',
      'server died', 'server dies', 'refused', 'connection', 'cannot connect', 'could not connect',
      'no response', 'does not respond', 'hang', 'hangs', 'hanging', 'hang forever', 'timeout',
      'timed out', 'not established', 'failed to connect', 'connection fails', 'disconnect',
      'websocket']),
    ('lifecycle/concurrency',
     ['cancel scope', 'asyncexitstack', 'event loop', 'coroutine', 'task group', 'cleanup',
      'race condition', 'concurrent', 'race', 'thread', 'deadlock', 'context manager',
      'with statement', 'shutdown', 'multiple session', 'lifespan', 'cancellederror',
      'generatorexit', 'cancellation', 'asyncio', 'await', 'reentrancy', 'double close',
      'clean up']),
    ('serialisation/parsing',
     ['json', 'serialize', 'serialization', 'parse', 'jsonrpcmessage', 'base64', 'decode',
      'utf-8', 'utf8', 'schema', 'pydantic', 'validation', 'nan', 'inf', 'structured content',
      'non-finite', 'bytes', 'typeerror', 'field alias', 'syntax error', 'syntaxerror',
      'unexpected token', 'non-utf8']),
    ('discovery/routing',
     ['unknown tool', 'unknown resource', 'no_such_tool', 'tool not found', 'not exposed',
      'cannot find', 'load the server', 'list_tools', 'listtools', 'discovery', 'route',
      'resource template', 'resource_template', 'dynamic resource', 'register', 'registering',
      'tool discovery', 'no such tool', 'resource']),
    ('protocol/spec',
     ['protocol', 'spec', 'method not found', 'json-rpc', 'jsonrpc', 'notification',
      'initialize', 'capabilit', 'message id', 'request id', 'protocol-version',
      'protocol_version', 'header', 'mismatch', '-326', '405', '404', 'id:null', 'null id',
      'envelope', 'compliance', 'conformance', 'rpc', 'should be', 'must be', 'spec']),
    ('error handling/reporting',
     ['error message', 'is_error', 'iserror', 'exception', 'traceback', 'raise', 'swallow',
      'silent', 'generic error', 'internal server error', 'mask', 'log level', 'logging',
      'sanitiz', 'sensitive', 'error code', 'err ']),
    ('external-dependency',
     ['inspector', 'claude desktop', 'desktop app', 'ui tool', 'mcp inspector', 'puppeteer',
      'elastic', 'third-party', 'external tool', 'server-github', 'frontend', 'web app',
      'extension']),
    ('environment/packaging',
     ['pip install', 'pip3', 'npx', 'node not found', 'pyproject', 'spawn ', 'enospc',
      'importerror', 'modulenotfound', 'module', 'package', 'dependency', 'venv', 'virtualenv',
      'uv run', 'uvx', 'wheel', 'dll', 'python version', 'python3', 'does not install',
      'installation', 'cannot install', 'command not found', 'enotfound', 'path', 'executable',
      'binary']),
    ('example/demo',
     ['example', 'demo', 'quickstart', 'sample server', 'hello world', 'examples/',
      'tutorial', 'getting started', 'simple server', 'basic example']),
]


def infer(title, body):
    """Classify from the title first (cleanest signal); fall back to body only if the
    title gives no match. Returns 'unknown' if nothing strong matches."""
    for source in (title, body):
        text = (source or '').lower()
        for nature, kws in TITLE_RULES:
            for kw in kws:
                if kw in text:
                    return nature
    return 'unknown'


def main():
    conf = json.load(open(CONF, encoding='utf-8'))
    fixed = set(json.load(open(FIXED, encoding='utf-8'))['removed_issues'])
    an = json.load(open(AN, encoding='utf-8'))
    repro_issues = set(b['issue'] for b in an['tier_b']['per_bug'])
    labels = json.load(open(LABELS, encoding='utf-8'))
    lmap = {x['number']: x for x in labels}

    active = [c for c in conf if c['number'] not in fixed]
    nonrepro = [c for c in active if c['number'] not in repro_issues]

    rows = []
    for c in nonrepro:
        n = c['number']
        lb = lmap.get(n, {})
        body = lb.get('body') or ''
        nature = infer(c.get('title', ''), body)
        rows.append({
            'issue': n,
            'origin': lb.get('origin', ''),     # start layer (already labelled)
            'nature': nature,                   # fault nature inferred from body (or unknown)
            'title': c.get('title', ''),
            'body_head': (body[:200] if body else ''),
        })

    dist = Counter(r['nature'] for r in rows)
    unknown_n = dist.get('unknown', 0)
    rows_sorted = sorted(rows, key=lambda r: (r['origin'], r['issue']))

    out = os.path.join(FP, 'fault_nature_293.json')
    json.dump({'items': rows_sorted, 'nature_dist': dict(dist), 'n': len(rows_sorted),
               'unknown_count': unknown_n},
              open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    L = []
    L.append('# Fault-nature classification of the 293 not-reproduced bugs')
    L.append('')
    L.append('> Inferred from each issue\'s body/title (no runtime evidence exists). Only '
             'determinable natures are assigned; ambiguous bugs are left as `unknown`. '
             'This is a fault-NATURE taxonomy, NOT the exposure channel and NOT the Taraghi '
             'taxonomy (deliberately unused).')
    L.append('')
    L.append('## Distribution (n=%d)' % len(rows_sorted))
    L.append('')
    L.append('| Fault nature | # | % of 293 |')
    L.append('|---|---:|---:|')
    for k, v in dist.most_common():
        L.append(f'| {k} | {v} | {100*v/len(rows_sorted):.1f}% |')
    L.append('')
    L.append(f'> `unknown` = {unknown_n} bugs whose body/title did not match any nature '
             'category; left blank rather than guessed.')
    L.append('')
    L.append('## Per-bug table')
    L.append('')
    L.append('| Issue | Origin | Fault nature | Title |')
    L.append('|---|---|---|---|')
    for r in rows_sorted:
        L.append(f"| {r['issue']} | {r['origin']} | {r['nature']} | {r['title'][:70]} |")
    L.append('')
    L.append('## Prose')
    L.append('')
    L.append(
        f'For the {len(rows_sorted)} active bugs we could not reproduce, we still classify the '
        f'fault NATURE from each issue\'s description (there is no runtime evidence). '
        f'This is a description-based nature taxonomy, distinct from the exposure channel '
        f'(which needs runtime evidence) and deliberately independent of the Taraghi taxonomy. '
        f'Only natures that are determinable from the description are assigned; '
        f'{unknown_n} ambiguous bugs are left unclassified rather than guessed.')

    md = os.path.join(DOCS, 'FAULT_NATURE_293.md')
    with open(md, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L))

    print('->', out)
    print('->', md)
    print('N=', len(rows_sorted), '| unknown=', unknown_n)
    print('DIST:', dict(dist))


if __name__ == '__main__':
    main()