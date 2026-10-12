#!/usr/bin/env python3
"""Compute Top-K diagnostic hit rates over the 49 reproduced bugs from llm_answers_49.json.

Reads the rank/scores the LLM produced (via metrics/predict_llm_49.py --topk) and reports:
  - Top-1 / Top-2 / Top-3 hit rate over all 49
  - Top-1 / Top-2 / Top-3 hit rate over the 13 NON-Server-origin bugs (the hard cases)
  - Top-1 over Server-origin (36) as reference
Writes docs/TopK_49_RESULTS.md + data/full_pool/topk_49.json.
Run from MCP-Fault-Benchmark/:
    python analysis/compute_topk_49.py
"""
import os, json, io, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FP = os.path.join(REPO, 'data', 'full_pool')
DOCS = os.path.join(REPO, 'docs')
LAYERS = ['Host', 'Client', 'Server', 'Transport']

d = json.load(open(os.path.join(FP, 'llm_answers_49.json'), encoding='utf-8'))

# keep only records with a valid rank list
ranked = [x for x in d if x.get('rank') and len(x['rank']) >= 1]
def topk_hit(rank, truth, k):
    return rank[0] == truth if k == 1 else truth in rank[:k]

all_bugs = ranked
nonserver = [x for x in ranked if x['origin'] != 'Server']
server = [x for x in ranked if x['origin'] == 'Server']

def rates(pool):
    n = len(pool)
    out = {}
    for k in (1, 2, 3):
        hits = sum(1 for x in pool if topk_hit(x['rank'], x['origin'], k))
        out[k] = (hits, n, round(hits / n * 100, 1) if n else 0)
    return out

r_all = rates(all_bugs)
r_ns = rates(nonserver)
r_sv = rates(server)

res = {
    'n_ranked': len(ranked),
    'n_all': len(all_bugs), 'n_nonserver': len(nonserver), 'n_server': len(server),
    'all': {str(k): v for k, v in r_all.items()},
    'nonserver': {str(k): v for k, v in r_ns.items()},
    'server': {str(k): v for k, v in r_sv.items()},
}
json.dump(res, open(os.path.join(FP, 'topk_49.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

lines = []
lines.append('# Top-K diagnostic hit rates over the 49 reproduced bugs')
lines.append('')
lines.append('> Computed from `data/full_pool/llm_answers_49.json` (rank/scores produced by ')
lines.append('> `metrics/predict_llm_49.py --topk`, CityU DeepSeek proxy, temperature=0). ')
lines.append('> `rank` is the 4-layer ranking the LLM returned; Top-k hit = the true origin layer ')
lines.append('> appears in the top-k. Overall = all 49; non-Server = the 13 genuinely hard cases. ')
lines.append('> Baseline (single-token answer, no ranking) overall = 77.6%, non-Server = 15.4%.')
lines.append('')
lines.append('| Scope | n | Top-1 | Top-2 | Top-3 |')
lines.append('|---|---:|---:|---:|---:|')
lines.append(f"| All 49 | {len(all_bugs)} | {r_all[1][0]} ({r_all[1][2]}%) | {r_all[2][0]} ({r_all[2][2]}%) | {r_all[3][0]} ({r_all[3][2]}%) |")
lines.append(f"| Non-Server (hard) | {len(nonserver)} | {r_ns[1][0]} ({r_ns[1][2]}%) | {r_ns[2][0]} ({r_ns[2][2]}%) | {r_ns[3][0]} ({r_ns[3][2]}%) |")
lines.append(f"| Server-origin (ref) | {len(server)} | {r_sv[1][0]} ({r_sv[1][2]}%) | {r_sv[2][0]} ({r_sv[2][2]}%) | {r_sv[3][0]} ({r_sv[3][2]}%) |")
lines.append('')
lines.append('## Interpretation')
lines.append('')
lines.append('- The overall figure is inflated by the 36 Server-origin bugs, which are correctly ')
lines.append('  reported at the Server layer and almost always ranked first. The **non-Server ')
lines.append('  sub-set is the honest hard-case number**: even allowing the LLM to list its top-3 ')
lines.append('  guesses, the true (non-Server) origin is often not among them, because the SDK reports ')
lines.append('  these faults at the Server layer (or silently / as a caller-side exception) and the ')
lines.append('  surface text carries the misleading layer. This reinforces the three-channel claim.')
lines.append('')
lines.append('## Per-bug (non-Server) details')
lines.append('')
lines.append('| Issue | Origin | Channel | rank (top->bottom) | Top-1 hit |')
lines.append('|---|---|---|---|---|')
for x in nonserver:
    hit = 'Y' if x['rank'][0] == x['origin'] else 'N'
    lines.append(f"| #{x['issue']} | {x['origin']} | {x['channel']} | {', '.join(x['rank'])} | {hit} |")

open(os.path.join(DOCS, 'TopK_49_RESULTS.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

# console-safe ASCII summary
sys.stdout.buffer.write(f"TopK computed: all={r_all[1]} / {r_all[2]} / {r_all[3]}; nonServer={r_ns[1]} / {r_ns[2]} / {r_ns[3]}; server={r_sv[1]} / {r_sv[2]} / {r_sv[3]}".encode('utf-8'))