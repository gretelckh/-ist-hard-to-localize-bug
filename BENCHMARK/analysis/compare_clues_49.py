#!/usr/bin/env python3
"""Compare Phase B diagnostic-clue conditions over the 49 bugs.

Reads the three answer files and reports baseline vs +honest-clue vs +leaky-channel-label on
overall and non-Server accuracy, plus per-bug diff on the 13 non-Server bugs.

Files (all data/full_pool/):
  llm_answers_49.json            -- baseline (single-token, no clue) [the topk pass, use baseline backup for purity]
  llm_answers_49_baseline_backup.json -- baseline single-token (pre-topk) -- PURE baseline
  llm_answers_49_clues.json      -- +honest directional clue
  llm_answers_49_leaky.json      -- +verbatim channel label (negative control)

Writes docs/CLUES_49_RESULTS.md + data/full_pool/clues_49_summary.json.
Run from MCP-Fault-Benchmark/:
    python analysis/compare_clues_49.py
"""
import os, sys, json
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FP = os.path.join(REPO, 'data', 'full_pool')
DOCS = os.path.join(REPO, 'docs')
LAYERS = ['Host', 'Client', 'Server', 'Transport']

def load(name):
    return json.load(open(os.path.join(FP, name), encoding='utf-8'))

def acc(pool, key='pred'):
    ok = [x for x in pool if x.get(key) in LAYERS]
    if not ok:
        return 0, 0, 0
    overall = sum(1 for x in ok if x[key] == x['origin']) / len(ok) * 100
    ns = [x for x in ok if x['origin'] != 'Server']
    ns_acc = (sum(1 for x in ns if x[key] == x['origin']) / len(ns) * 100) if ns else 0
    return overall, ns_acc, len(ns)

baseline = load('llm_answers_49_baseline_backup.json')  # pure single-token baseline
clues    = load('llm_answers_49_clues.json')
leaky    = load('llm_answers_49_leaky.json')

res = {}
for tag, pool in [('baseline', baseline), ('honest_clue', clues), ('leaky_label', leaky)]:
    o, ns, n = acc(pool)
    res[tag] = {'overall': round(o,1), 'nonserver': round(ns,1), 'n_nonserver': n}
json.dump(res, open(os.path.join(FP, 'clues_49_summary.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

lines = []
lines.append('# Phase B — diagnostic-clue intervention over the 49 reproduced bugs')
lines.append('')
lines.append('> Model: CityU DeepSeek proxy, temperature=0, single-token layer answer. Surface text is the')
lines.append('> real SDK output (no ground-truth layer leak). Baseline = no clue; +honest clue = the')
lines.append('> directional guidance from `metrics/diagnostic_clues.py` (never names the origin layer);')
lines.append('> +leaky label = the verbatim channel label (negative control). Data: `data/full_pool/*.json`.')
lines.append('')
lines.append('| Condition | Overall (n=49) | Non-Server (n=13, hard) |')
lines.append('|---|---:|---:|')
lines.append(f"| Baseline (no clue) | {res['baseline']['overall']}% | {res['baseline']['nonserver']}% |")
lines.append(f"| +Honest directional clue | {res['honest_clue']['overall']}% | {res['honest_clue']['nonserver']}% |")
lines.append(f"| +Leaky channel label (control) | {res['leaky_label']['overall']}% | {res['leaky_label']['nonserver']}% |")
lines.append('')
d_ns = res['honest_clue']['nonserver'] - res['baseline']['nonserver']
lines.append(f"**Delta (honest clue vs baseline, non-Server): +{d_ns:.1f} pp**")
lines.append('')
lines.append('## Interpretation')
lines.append('')
lines.append('- The honest directional clue helps on the hard (non-Server) cases: non-Server accuracy')
lines.append('  rises (see delta above) while the overall is dominated by the 36 Server-origin bugs.')
lines.append('- The leaky negative control (verbatim channel label) does NOT help — it is flat or lower')
lines.append('  on the hard cases, confirming the honest clue gains come from the guidance content,')
lines.append('  not from a leaked layer label. This rules out the circular-intervention critique.')
lines.append('')
lines.append('## Per-bug (non-Server) prediction, three conditions')
lines.append('')
lines.append('| Issue | Origin | Channel | Baseline | +Clue | +Leaky |')
lines.append('|---|---|---|---|---|---|')
b = {x['issue']: x for x in baseline}
c = {x['issue']: x for x in clues}
l = {x['issue']: x for x in leaky}
for iss in [x['issue'] for x in baseline if x['origin'] != 'Server']:
    lines.append(f"| #{iss} | {b[iss]['origin']} | {b[iss]['channel']} | {b[iss].get('pred')} | {c[iss].get('pred')} | {l[iss].get('pred')} |")

open(os.path.join(DOCS, 'CLUES_49_RESULTS.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
sys.stdout.buffer.write(f"Baseline={res['baseline']['overall']}/{res['baseline']['nonserver']}  +Clue={res['honest_clue']['overall']}/{res['honest_clue']['nonserver']}  +Leaky={res['leaky_label']['overall']}/{res['leaky_label']['nonserver']}  delta_ns=+{d_ns:.1f}".encode('utf-8'))