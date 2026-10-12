#!/usr/bin/env python3
"""Migrate the diagnostic-clue tool (Phase B) from the OLD 80-run synthetic data to the 49
genuinely reproduced real bugs.

Reads the authoritative per-bug exposure channel (already human-classified) from
`data/full_pool/diag_dataset_49.json` (issue/origin/channel/surface_text) and emits a directional
hint (never names the root-cause layer) for each bug, into `data/full_pool/diag_clues_49.json`.

This mirrors metrics/diagnostic_clues.py but keys on the 49 real bugs. The channel is taken from
the ground truth (already classified by hand), NOT re-derived by regex, because the real bugs'
surface text is often too terse for the old regex to classify reliably.

Run from MCP-Fault-Benchmark/:
    python analysis/make_diag_clues_49.py
"""
import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FP = os.path.join(REPO, 'data', 'full_pool')

# Reuse the HINTS from the Phase B tool (same directional language, no layer name).
from metrics.diagnostic_clues import HINTS, HINTS_LEAKY

# Map the 49-bug channel labels -> the HINTS key that describes the right direction.
#   - pushed-server   -> pushed-server
#   - silent          -> silent
#   - caller-exception-> caller-exception
#   - single-layer-masked / single-layer-correct -> single-layer (defect inside the reported tool)
#   - registration-error -> registration (a NEW hint; server fails to build/register a tool)
CHANNEL_MAP = {
    'pushed-server': 'pushed-server',
    'silent': 'silent',
    'caller-exception': 'caller-exception',
    'single-layer-masked': 'single-layer',
    'single-layer-correct': 'single-layer',
    'registration-error': 'registration',
}

# Extra directional hint for registration-time failures (server can't even start).
REG_HINT = (
    "CLUE: The failure occurred at SERVER REGISTRATION / BUILD time, before the server could start "
    "or serve any tool. The error is a raised Python exception (ValueError / AttributeError / "
    "PydanticSchemaGenerationError) thrown while the SDK built the tool/resource registry from the "
    "handler definitions. This is a definition/signature problem, not a runtime call problem: "
    "inspect the handler's parameters, annotations, return type, and any URI template variables the "
    "decorator binds, and check the SDK version. The server never comes up, so no client error is "
    "the real signal; the traceback at construction is the diagnostic evidence."
)

ds = json.load(open(os.path.join(FP, 'diag_dataset_49.json'), encoding='utf-8'))

rows = []
for r in ds:
    issue = r['issue']
    channel = r['channel']
    key = CHANNEL_MAP.get(channel)
    if key is None:
        key = 'no-evidence'
    if channel == 'registration-error':
        hint = REG_HINT
    else:
        hint = HINTS.get(key, '')
    leaky = HINTS_LEAKY.get(key, '') if channel != 'registration-error' else 'CLUE-CHANNEL: registration-error'
    rows.append({
        'issue': issue,
        'origin': r['origin'],
        'channel': channel,
        'hint': hint,
        'hint_leaky': leaky,
    })

out = os.path.join(FP, 'diag_clues_49.json')
json.dump(rows, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# Sanity: honest hint must never assert an ORIGIN layer.
origin_assert = ['origin is Host', 'origin is Client', 'origin is Server', 'origin is Transport',
                 'originated in Host', 'originated in Client', 'originated in Server',
                 'originated in Transport', 'root cause is Host', 'root cause is Client',
                 'root cause is Server', 'root cause is Transport', 'the true origin is']
bad = [r for r in rows if any(p.lower() in r['hint'].lower() for p in origin_assert)]
print(f'Wrote {len(rows)} bugs -> data/full_pool/diag_clues_49.json')
print('Channel distribution:')
from collections import Counter
for ch, n in Counter(r['channel'] for r in rows).most_common():
    print(f'  {ch:<22s} {n}')
print(f'Sanity check (honest hint must NOT assert ORIGIN layer): asserts={len(bad)}')
for r in bad[:10]:
    print('   LEAK!', r['issue'], '->', r['hint'][:80])
if bad:
    sys.exit('ABORT: a hint asserts an origin layer; fix before proceeding.')
print('OK: no origin-layer assertion in honest hints.')