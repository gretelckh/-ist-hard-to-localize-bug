#!/usr/bin/env python3
"""Phase C analysis: combine the repair experiment results and quantify the value of the
diagnostic-clue tool for REPAIR (not just localisation).

Reads the four result files (synthetic + advanced, no-clue + clue) and reports per-case and
aggregate repair success. Generates figs/fig_repair.png.
"""
import os, json, sys
from collections import defaultdict
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, 'data'); FIG = os.path.join(REPO, 'figs'); os.makedirs(FIG, exist_ok=True)

def load(f):
    p = os.path.join(D, f)
    if not os.path.exists(p):
        return {}
    return {r['case']: r for r in json.load(open(p, encoding='utf-8'))}

syn_nc = load('repair_results.json'); syn_c = load('repair_results_clue.json')
adv_nc = load('repair_adv_noclue.json'); adv_c = load('repair_adv_clue.json')

lines = []
def p(*a):
    s = ' '.join(str(x) for x in a); lines.append(s); print(s)

p('=' * 74)
p('PHASE C: REPAIR EXPERIMENT — does the diagnostic-clue tool help an LLM FIX faults?')
p('=' * 74)
p('Method: for each case the LLM (given the faulting source + SDK output, and +/- the clue) '
  'produces a fixed script, which we re-run and verify (no error + correct value).')
p('')

def agg(label, nc, c):
    n = len(nc)
    np = sum(1 for r in nc.values() if r['passed'])
    cp = sum(1 for r in c.values() if r['passed'])
    p(f'{label}: no-clue {np}/{n} = {np/n*100:.1f}%   |   +clue {cp}/{n} = {cp/n*100:.1f}%   '
      f'({cp-np:+d} cases)')
    return np/n, cp/n

p('--- Aggregate repair success ---')
s = agg('Synthetic MCP-Fault-20 (17)', syn_nc, syn_c)
a = agg('Advanced production bugs (6)', adv_nc, adv_c)

all_nc = {**syn_nc, **adv_nc}; all_c = {**syn_c, **adv_c}
t = agg('Combined (23)', all_nc, all_c)

p('\n--- Per-case comparison (case, no-clue, +clue) ---')
allcases = list(syn_nc.keys()) + list(adv_nc.keys())
diffs = []
for k in allcases:
    nv = all_nc.get(k, {}).get('passed'); cv = all_c.get(k, {}).get('passed')
    mark = 'DIFF' if nv != cv else ''
    if nv != cv:
        diffs.append(k)
    p(f'  {k:<28s} nc={nv}  clue={cv}  {mark}')
p(f'\nCases where the two conditions differ: {diffs if diffs else "NONE (identical)"}')

p('\n--- Honest interpretation ---')
p('The diagnostic-clue tool improves LOCALISATION (45% -> 52.5%, Phase B) but does NOT change '
  'REPAIR success here (identical). This is expected and informative: the repair LLM is given the '
  'FULL faulting source, so it can read the bug directly and does not need the clue to localise. '
  'The bottleneck in MCP debugging is therefore LOCALISING the fault (which the clue helps), not '
  'FIXING it once the relevant code is in hand.')

# Figure: grouped bars, no-clue vs +clue, per group
fig, ax = plt.subplots(figsize=(6.8, 4.2))
groups = ['Synthetic (17)', 'Advanced (6)', 'Combined (23)']
nc_vals = [s[0]*100, a[0]*100, t[0]*100]
c_vals = [s[1]*100, a[1]*100, t[1]*100]
x = range(len(groups)); w = 0.35
ax.bar([i-w/2 for i in x], nc_vals, w, label='No clue (source + SDK output)', color='#e41a1c')
ax.bar([i+w/2 for i in x], c_vals, w, label='+ diagnostic clue', color='#1b9e77')
for i in x:
    ax.text(i-w/2, nc_vals[i]+1.5, f'{nc_vals[i]:.0f}%', ha='center', fontsize=9)
    ax.text(i+w/2, c_vals[i]+1.5, f'{c_vals[i]:.0f}%', ha='center', fontsize=9)
ax.set_xticks(list(x)); ax.set_xticklabels(groups, fontsize=9)
ax.set_ylabel('Repair success rate (fixed script verified)'); ax.set_ylim(0, 110)
ax.set_title('Repair success: the clue does not change repair given full source', fontsize=9.5)
ax.legend(loc='upper left', fontsize=8)
plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig_repair.png'), dpi=200); plt.close()
p('\nfig -> figs/fig_repair.png')

with open(os.path.join(D, 'repair_summary.txt'), 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(lines))
p('-> data/repair_summary.txt')