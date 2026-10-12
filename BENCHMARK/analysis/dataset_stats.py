#!/usr/bin/env python3
"""Dataset statistics for the ACTIVE (350) bug dataset.

Re-derives the authoritative numbers used in the paper's sec:sampling:
  - total active bugs (398 confirmed - 48 fixed-in-2.2.0 = 350)
  - four-layer origin distribution (Server/Client/Transport/Host)
  - open / closed counts
  - reproduced count (T1)

Source of truth:
  - data/full_pool/origin_labels.json  (398 bugs + expert origin layer)
  - data/full_pool/fixed_removed.json  (48 bugs already fixed in mcp 2.2.0 -> removed)
  - data/repro_progress.json           (reproduction status, for the T1 count)

This makes the sec:sampling numbers reproducible (no re-analysis by hand).

Run from MCP-Fault-Benchmark/:
    python analysis/dataset_stats.py
"""
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, '..', 'data', 'full_pool'))
ORIG = os.path.join(BASE, 'origin_labels.json')
FIXED = os.path.join(BASE, 'fixed_removed.json')
CONF = os.path.join(BASE, 'confirmed_bugs.json')
PROG = os.path.join(BASE, '..', 'repro_progress.json')


def main():
    orig = json.load(open(ORIG, encoding='utf-8'))
    fixed = set(json.load(open(FIXED, encoding='utf-8'))['removed_issues'])
    conf = {x['number']: x for x in json.load(open(CONF, encoding='utf-8'))}
    prog = json.load(open(PROG, encoding='utf-8'))

    active = [r for r in orig if r['number'] not in fixed]
    total = len(active)

    layer = Counter(r['origin'] for r in active)
    states = Counter(conf.get(r['number'], {}).get('state') for r in active)
    # reproduced = done & defect_captured in repro_progress, or in the verified set
    reproduced = [r for r in active
                  if prog.get(str(r['number']), {}).get('status') == 'done'
                  and prog.get(str(r['number']), {}).get('defect_captured')]

    print('ACTIVE dataset: %d bugs (398 confirmed - %d fixed-in-2.2.0)' % (total, len(fixed)))
    print('  four-layer origin:', ', '.join('%s %d' % (k, v) for k, v in layer.items()))
    print('  open/closed: %d / %d' % (states.get('open', 0), states.get('closed', 0)))
    print('  reproduced (T1): %d' % len(reproduced))

    # Sanity: dump to a json for anyone re-using the numbers
    out = {
        'active_total': total,
        'removed_fixed': len(fixed),
        'confirmed_total': len(orig),
        'layer': dict(layer),
        'open': states.get('open', 0),
        'closed': states.get('closed', 0),
        'reproduced': len(reproduced),
    }
    outpath = os.path.join(BASE, 'dataset_stats.json')
    json.dump(out, open(outpath, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('->', outpath)


if __name__ == '__main__':
    main()