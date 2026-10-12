#!/usr/bin/env python3
"""Build the 49-bug diagnosis dataset (surface-text input) for the LLM diagnosis experiment.

For each of the 49 reproduced real bugs we take its REAL SDK output (from the raw capture)
and build an honest surface-text input (no ground-truth layer leak). This mirrors the
diagnosis task: given only the SDK output, predict the layer where the fault ORIGINATED.

Data source:
  - per-bug origin + channel: data/full_pool/active_dataset_analysis.json (tier_b.per_bug)
  - real SDK output: data/real_raw/real_{issue}.txt  OR  the real_r_*.txt referenced in
    data/full_pool/hard_to_localize_49.json (evidence).

Output:
  - data/full_pool/diag_dataset_49.json
    [ {issue, origin, channel, surface_text, file}, ... ]  (49 items)
  - prints the origin distribution.

Run from MCP-Fault-Benchmark/:
    python analysis/build_diag_dataset_49.py
"""
import os, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..'))
FP = os.path.join(REPO, 'data', 'full_pool')
RAW = os.path.join(REPO, 'data', 'real_raw')
AN = os.path.join(FP, 'active_dataset_analysis.json')
HL = os.path.join(FP, 'hard_to_localize_49.json')

# same leaky-layer stripping as the old experiment (there are no case headers here, but keep
# the function for consistency / in case a raw file contains a layer name)
LEAKY = ['故障类型', 'Transport传输层', 'Host调度层', 'Client报文层', 'Server工具层']


def surface_text(txt):
    """Build an honest surface-text input (no layer leak)."""
    for line in txt.splitlines():
        ls = line.strip()
        if 'meta=' in ls and 'io.modelcontextprotocol' in ls:
            return ls
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    useful = [l for l in lines
              if not any(k in l for k in LEAKY) and not set(l) <= set('=-')]
    return ' | '.join(useful) if useful else (lines[0] if lines else '')


def main():
    an = json.load(open(AN, encoding='utf-8'))
    per = an['tier_b']['per_bug']
    hl = json.load(open(HL, encoding='utf-8'))
    # issue -> evidence (to find real_r file)
    ev_map = {r['issue']: r['evidence'] for r in hl['items']}

    rows = []
    missing = []
    for b in per:
        i = b['issue']
        ev = ev_map.get(i, '')
        m = re.search(r'(real_r_\w+\.txt)', ev)
        fname = m.group(1) if m else f'real_{i}.txt'
        path = os.path.join(RAW, fname)
        if not os.path.exists(path):
            missing.append((i, fname))
            txt = b.get('note', '')
        else:
            txt = open(path, encoding='utf-8', errors='replace').read()
        rows.append({
            'issue': i,
            'origin': b['origin'],
            'channel': b['channel'],
            'surface_text': surface_text(txt),
            'file': fname,
        })

    out = os.path.join(FP, 'diag_dataset_49.json')
    json.dump(rows, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    from collections import Counter
    print('->', out)
    print('N =', len(rows))
    print('origin dist:', dict(Counter(r['origin'] for r in rows)))
    print('missing files:', missing)


if __name__ == '__main__':
    main()