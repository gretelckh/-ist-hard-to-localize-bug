#!/usr/bin/env python3
"""Induce a 'hard-to-localise reason' for each of the 49 reproduced bugs from its
ACTUAL reported error text (the SDK output), not from a preset category.

For every bug we read the runtime evidence (note) and ask: *why is this bug hard to
localise?* The observed error/behaviour patterns converge into a small set of reasons.

Reason set (induced from the evidence, not assumed):
  - genericised     : a generic message replaces the real root cause
                      ('Error executing tool X' / 'Internal server error' / 'Invalid structured content')
  - silent-ok       : a success / no-error result is returned although a logical error occurred
                      (is_error=False, HTTP 200, value looks valid)
  - caller-exception: a bare exception is raised in the calling code, outside the server context
  - insufficient    : reported at the correct layer but only a vague 'Unknown X' (no precise cause)
  - registration    : the server fails to build / register a tool at startup

Outputs:
  - data/full_pool/hard_to_localize_49.json  (per-bug origin, channel, reason, evidence)
  - docs/HARD_TO_LOCALIZE_49.md              (table + induced distribution + prose)

Run from MCP-Fault-Benchmark/:
    python analysis/analyze_hard_to_localize.py
"""
import os, json
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..'))
FP = os.path.join(REPO, 'data', 'full_pool')
DOCS = os.path.join(REPO, 'docs')
AN = os.path.join(FP, 'active_dataset_analysis.json')
os.makedirs(DOCS, exist_ok=True)


def induce(note):
    """Classify the hard-to-localise reason from the reported error text."""
    n = note.lower()
    # 1) bare exception in caller, outside server context
    if 'exceptiongroup' in n or 'http 400' in n or '-32602' in n or 'timeout' in n:
        return 'caller-exception'
    # 2) server fails to build / register at startup
    if 'raised-at-reg' in n or 'at registration' in n:
        return 'registration'
    # 3) reported at the right layer but only a vague 'Unknown X'
    if ('unknown tool' in n or 'unknown resource' in n or 'no_such_tool' in n) \
            and ('is_error=true' in n or 'mcperror' in n):
        return 'insufficient'
    # 4) silent: success / no-error result despite a logical error
    if ('is_error=false' in n or 'is_error:false' in n or 'is_error=false' in n
            or 'http 202' in n or 'http 200' in n or 'never rejected' in n
            or 'not validated' in n or 'accepted as notification' in n
            or 'wrong result shape' in n):
        return 'silent-ok'
    # 5) genericised: a generic message hides the real cause
    if ('executing tool' in n or 'internal server error' in n
            or 'invalid structured content' in n):
        return 'genericised'
    return 'unclassified:' + note[:40]


def main():
    an = json.load(open(AN, encoding='utf-8'))
    per = an['tier_b']['per_bug']

    rows = []
    for b in per:
        rows.append({
            'issue': b['issue'],
            'origin': b['origin'],          # start layer
            'channel': b['channel'],        # exposure layer / channel
            'reason': induce(b['note']),    # why hard to localise (induced from evidence)
            'evidence': b['note'],
        })

    dist = Counter(r['reason'] for r in rows)
    rows_sorted = sorted(rows, key=lambda r: (r['origin'], r['issue']))

    out = os.path.join(FP, 'hard_to_localize_49.json')
    json.dump({'items': rows_sorted, 'reason_dist': dict(dist), 'n': len(rows_sorted)},
              open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    # --- markdown ---
    L = []
    L.append('# Hard-to-localise reasons (49 reproduced bugs)')
    L.append('')
    L.append('> Induced from each bug\'s actual reported error (evidence), not from a preset '
             'category. Data: `data/full_pool/hard_to_localize_49.json`.')
    L.append('')
    L.append('| Issue | Origin (start) | Exposure (channel) | Hard-to-localise reason | Evidence |')
    L.append('|---|---|---|---|---|')
    for r in rows_sorted:
        L.append(f"| {r['issue']} | {r['origin']} | {r['channel']} | {r['reason']} | {r['evidence']} |")
    L.append('')
    L.append('## Distribution')
    L.append('')
    for k, v in dist.most_common():
        L.append(f'- {v}: {k}')
    L.append('')
    L.append('## Prose')
    L.append('')
    L.append(
        'Reading the reported error of each of the 49 reproduced bugs, we ask why it is hard to '
        'localise. The reasons converge into a small set. The dominant one is that a generic '
        'message replaces the real root cause (e.g. `Error executing tool X`, `Internal server '
        'error`, `Invalid structured content`), so even when the bug is reported at the correct '
        'layer the precise cause is erased. A second class is fully silent: the SDK returns a '
        'success / no-error result (`is_error=False`, HTTP 200, or a plausible value) despite a '
        'logical error. A smaller set surfaces as a bare caller-side exception outside the server '
        'context, or reports only a vague `Unknown X` with no precise cause, and a few fail at '
        'registration time before the server can start.')
    L.append('')

    md = os.path.join(DOCS, 'HARD_TO_LOCALIZE_49.md')
    with open(md, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L))

    print('->', out)
    print('->', md)
    print('DISTRIBUTION:', dict(dist))
    print('TOTAL:', len(rows_sorted))


if __name__ == '__main__':
    main()