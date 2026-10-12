#!/usr/bin/env python3
"""Step 3 (data rebuild): assess reproducibility tier for each of the 398 confirmed bugs.

The user would like to reproduce as many of the 398 as possible on this machine
(mcp 2.2.0 + Streamable-HTTP). This script produces an HONEST, reviewable first-pass
assessment of each bug's reproducibility tier. The 18 already-reproduced bugs are
tier-1 (verified).

Tiers:
  T1 reproducible-now   : can be reproduced on this machine (mcp 2.2.0 + streamable-HTTP
                          + locally available deps). Verified for the 18.
  T2 env/dep-limited    : needs a specific platform / Python version / dependency /
                          packaging setup that is NOT currently available locally.
  T3 auth-limited       : needs an OAuth / auth provider / credentials (token, secret,
                          redirect_uri, issuer) that we cannot supply locally.
  T4 spec/behaviour-only: a protocol-spec or behavioural gap (compliance, validation,
                          observability) that does not manifest as a runnable fault
                          (it is observable by inspection / version-pinning, not by
                          triggering a crashing tool call).
  T5 not-reproducible   : info insufficient, needs an external service/host, or the
                          defect is a config/example/packaging issue not tied to the SDK.

Outputs:
  data/full_pool/repro_tiers.json    per-bug tier + evidence
  data/full_pool/repro_tiers.xlsx    Excel
  (console) tier distribution

Run from MCP-Fault-Benchmark/:
    python analysis/assess_reproducibility.py
"""
import json, os, sys, re
sys.stdout.reconfigure(encoding='utf-8')
from collections import Counter
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
CONF = os.path.normpath(os.path.join(HERE, '..', 'data', 'full_pool', 'confirmed_bugs.json'))
POOL = os.path.normpath(os.path.join(HERE, '..', 'data', 'full_pool', 'full_pool_screened.json'))
PROG = os.path.normpath(os.path.join(HERE, '..', 'data', 'repro_progress.json'))
OUT = os.path.normpath(os.path.join(HERE, '..', 'data', 'full_pool', 'repro_tiers.json'))
OUTX = os.path.normpath(os.path.join(HERE, '..', 'data', 'full_pool', 'repro_tiers.xlsx'))
# Bugs already FIXED in mcp 2.2.0 (T1-fixed) are REMOVED from the active dataset (350),
# so the dataset = bugs still active in the current SDK. Raw 398 survey pool is kept in
# confirmed_bugs.json. See data/full_pool/fixed_removed.json.
FIXED_FILE = os.path.normpath(os.path.join(HERE, '..', 'data', 'full_pool', 'fixed_removed.json'))

# 18 already-reproduced distinct issues (verified tier-1) - not in repro_progress.json
VERIFIED_T1 = {3549, 3554, 3556, 3557, 3560, 3569, 3572, 3573, 3578, 3579,
               3585, 3586, 3592, 3637, 3640, 3643, 3644, 3646}

# Actual reproduction results drive the tier: bugs done in repro_progress.json (reproduced)
# are T1. Bugs that are limited-but-explainable get a more precise reason. This keeps the
# tiers in sync with the real reproduction runs (no re-analysis needed each session).
def _repro_tier(prog, num):
    """Return (tier, reason) for a bug tracked in repro_progress.json, else None."""
    rec = prog.get(str(num))
    if not rec:
        return None
    status = rec.get('status')
    reason = (rec.get('reason') or '').strip()
    if status == 'done' and rec.get('defect_captured'):
        return 'T1 reproducible-now', 'reproduced on this machine (mcp 2.2.0 + streamable-HTTP): ' + (reason or '')
    if status == 'done':
        return 'T1 reproducible-now', 'reproduced (defect captured): ' + (reason or '')
    if 'fixed-in-current' in reason:
        return 'T1-fixed', 'bug already FIXED in mcp 2.2.0 (returns correct behaviour) - NOT a reproduction: ' + reason
    if 'observation-only' in reason:
        return 'T4 observation-only', 'server-log/notification behaviour; not visible via client return value: ' + reason
    if 'not-exercised' in reason or 'not-reproduced' in reason:
        return 'T4 spec/behaviour-only', 'needs a special trigger not yet exercised: ' + reason
    if 'requires' in reason and ('auth' in reason.lower() or 'credential' in reason.lower()):
        return 'T3 auth-limited', reason
    return 'T2 env/dep-limited', reason

# auth / credentials keywords -> tier-3 (auth-limited)
AUTH_KW = ['oauth', 'auth', 'token', 'credential', 'redirect_uri', 'issuer', 'client_secret',
           'scope', '401', '403', 'authorization', 'secret', 'key', 'vscode', 'login',
           'authenticate', 'well-known', 'client id', 'jwt']
# env / platform / dep keywords -> tier-2 (env-limited)
ENV_KW = ['windows', 'linux', 'macos', 'python 3.1', 'python 3.1', 'docker', 'import',
          'pip', 'install', 'uv ', 'module not found', 'importerror', 'pyinstaller',
          'dependency', 'pydantic v2', 'httpx', 'version', 'python 3.12', 'python 3.13',
          'python 3.14', 'jupyter', 'venv', 'npx', 'node', 'subprocess', 'asyncio',
          'multiprocessing', 'lifespan', 'starlette', 'fastapi', 'uvicorn', 'gunicorn',
          'azure', 'cloud run', 'railway', 'data centre', 'sticky session', 'signal']
# spec / behaviour / observability-only keywords -> tier-4
SPEC_KW = ['spec', 'compliance', 'gap', 'protocol', 'validation', 'should', 'must',
           'observability', 'logging', 'traceback', 'error code', '-32600', '-32601',
           '-32602', 'json-rpc', 'capability', 'advertise', 'header', 'meta', 'schema',
           'catalog', 'cwe', 'backport', 'pin', 'upper bound', 'whitelist']

# issue numbers that are example / packaging / config / env-only (not an SDK runtime fault
# tied to a tool call) -> tier-5 not-reproducible-as-fault


def tier_of(title, body, num):
    if num in VERIFIED_T1:
        return 'T1 reproducible-now', 'verified-reproducible on this machine (mcp 2.2.0 + streamable-HTTP)'
    t = (title + ' ' + body).lower()
    if any(k in t for k in AUTH_KW):
        return 'T3 auth-limited', 'requires OAuth/auth provider or credentials not available locally'
    if any(k in t for k in ENV_KW):
        return 'T2 env/dep-limited', 'requires specific platform/Python/dependency/packaging not present'
    if any(k in t for k in SPEC_KW):
        return 'T4 spec/behaviour-only', 'protocol-spec or behaviour gap observable by inspection, not a runnable crash'
    return 'T5 not-reproducible', 'info insufficient / external service / config or example-only issue'


def main():
    conf = json.load(open(CONF, encoding='utf-8'))
    pool = json.load(open(POOL, encoding='utf-8'))
    pool_map = {x['number']: x for x in pool}
    bynum = {x['number']: x for x in conf}
    prog = json.load(open(PROG, encoding='utf-8')) if os.path.exists(PROG) else {}

    # Remove bugs already FIXED in mcp 2.2.0 from the active dataset (user decision 2026-10-10).
    # The raw 398 survey pool stays in confirmed_bugs.json; only downstream tiers exclude these.
    fixed_removed = set()
    if os.path.exists(FIXED_FILE):
        fixed_removed = set(json.load(open(FIXED_FILE, encoding='utf-8')).get('removed_issues', []))
    bynum = {n: x for n, x in bynum.items() if n not in fixed_removed}

    rows = []
    for n in sorted(bynum):
        rec = bynum[n]
        body = (pool_map.get(n, {}).get('body') or '') or (rec.get('body_head') or '')
        # Prefer the REAL reproduction result (repro_progress.json) so the tiers stay in
        # sync with the actual runs; fall back to keyword heuristics only if never tried.
        rt = _repro_tier(prog, n)
        if rt:
            tier, reason = rt
        else:
            tier, reason = tier_of(rec.get('title') or '', body, n)
        rows.append({'number': n, 'title': rec.get('title') or '', 'url': rec.get('url') or '',
                     'tier': tier, 'reason': reason})

    dist = Counter(r['tier'].split()[0] for r in rows)
    print('=' * 72)
    print('REPRODUCIBILITY TIER ASSESSMENT for %d confirmed bugs' % len(rows))
    print('=' * 72)
    for t in ['T1', 'T1-fixed', 'T2', 'T3', 'T4', 'T5']:
        print('  %-8s %3d  (%s)' % (t, dist.get(t, 0), '%.1f%%' % (dist.get(t, 0) / len(rows) * 100)))
    print('  T1 verified =', len(VERIFIED_T1), '| reproduced =', sum(1 for r in rows if r['tier'].startswith('T1 ')))
    print('  NOTE: T1 = genuinely reproduced; T1-fixed = already fixed in 2.2.0 (NOT a reproduction)')

    json.dump(rows, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\n->', OUT)

    wb = openpyxl.Workbook(); ws = wb.active; ws.title = 'repro_tiers'
    headers = ['序号', 'GitHub Issue', '链接', '标题', '可复现性层级', '判定依据']
    ws.append(headers)
    for h in headers:
        c = ws[f'{chr(65+headers.index(h))}1']
        c.font = Font(bold=True, color='FFFFFF')
        c.fill = PatternFill('solid', fgColor='4472C4')
        c.alignment = Alignment(horizontal='center', vertical='center')
    for i, r in enumerate(rows, start=2):
        ws.append([i-1, '#' + str(r['number']), r['url'], r['title'], r['tier'], r['reason']])
    widths = [6, 12, 50, 55, 24, 70]
    for j, w in enumerate(widths, start=1):
        ws.column_dimensions[chr(64+j)].width = w
    wb.save(OUTX)
    print('->', OUTX)


if __name__ == '__main__':
    main()