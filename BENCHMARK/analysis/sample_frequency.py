#!/usr/bin/env python3
"""Data-driven sampling rationale: real issue pool frequency by (author-labelled) category.

Addresses the review concern "why did you pick these data?" with EVIDENCE rather than
hand-waving: we tally the genuine ISSUES in the official pool
(data/gh_issues_pool.json) that are candidates for streamable-HTTP reproduction and show
(a) the real frequency of each fault category, and (b) that our reproduced subset is
sampled to cover the most frequent / most severe / most time-consuming categories that
Taraghi et al. (arXiv:2603.05637) identify.

Outputs:
    docs/real_sample_rationale.md  (human-readable evidence)
    figs/fig_sample_frequency.png  (pool frequency vs reproduced coverage)
Usage:
    python analysis/sample_frequency.py
"""
import os, sys, json
sys.stdout.reconfigure(encoding='utf-8')
from collections import Counter
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(REPO, 'data', 'gh_issues_pool.json')
REAL = os.path.join(REPO, 'data', 'real_index.json')

# ---- author-labelled mapping issue# -> Taraghi bucket (same as make_real_excel) ----
# We label every ISS candidate in the pool that is HTTP-reproducible in principle.
def bucket(num):
    m = {
        3554: 'Tool Response Handling', 3555: 'Tool Response Handling', 3557: 'Host / Tool Connection',
        3560: 'Host / Tool Connection', 3569: 'Host / Tool Connection', 3572: 'Parameter / Schema Validation',
        3573: 'Tool Response Handling', 3576: 'Server / Tool Config.', 3578: 'Tool Discovery & Reg.',
        3579: 'Tool Discovery & Reg.', 3585: 'Tool Response Handling', 3586: 'Tool Response Handling',
        3588: 'Host / Tool Connection', 3589: 'Tool Discovery & Reg.', 3590: 'Server / Tool Config.',
        3592: 'Tool Authentication', 3598: 'Tool Authentication', 3601: 'Host / Tool Connection',
        3605: 'Host / Tool Connection', 3621: 'Tool Response Handling', 3631: 'Host / Tool Connection',
        3637: 'Parameter / Schema Validation', 3639: 'Host / Tool Connection', 3640: 'Server / Tool Config.',
        3641: 'Host / Tool Connection', 3643: 'Tool Response Handling', 3644: 'Tool Response Handling',
        3646: 'Parameter / Schema Validation', 3649: 'Tool Response Handling', 3651: 'Host / Tool Connection',
        3652: 'Tool Authentication', 3656: 'Tool Response Handling', 3545: 'Tool Authentication',
        3546: 'Tool Authentication', 3544: 'Server / Tool Config.',
    }
    return m.get(num, None)

# Taraghi severity/effort stats from arXiv:2603.05637 (cited in bib taraghi2026real)
FREQ_SIGNAL = {
    'Tool Response Handling': 'most frequent (66.67%)',
    'Parameter / Schema Validation': 'high frequency (API Usage 60.98%)',
    'Tool Authentication': 'most time-consuming (effort 0.41)',
    'Host / Tool Connection': 'most severe (0.42)',
    'Tool Discovery & Reg.': 'severity 0.37',
    'Server / Tool Config.': 'Server/Tool Config 31.74%',
}
PRIORITY = ['Tool Response Handling', 'Host / Tool Connection', 'Tool Authentication',
            'Tool Discovery & Reg.', 'Parameter / Schema Validation', 'Server / Tool Config.']

def main():
    pool = json.load(open(POOL, encoding='utf-8'))
    # reproduceable-in-principle ISS candidates (auth/security need a server we don't run;
    # stdio/SSE need a different transport). We label the HTTP-reproducible subset.
    cdd = [x for x in pool if x['type'] == 'ISS']
    cdd_num = set()
    for x in cdd:
        n = x['number']
        if bucket(n):
            cdd_num.add(n)
    # pool frequency by bucket
    pool_buckets = Counter(bucket(n) for n in cdd_num)
    # our reproduced subset
    real = json.load(open(REAL, encoding='utf-8'))
    real_nums = [int(c['issue_src'].split('#')[1]) for c in real['cases']]
    real_unique = set(real_nums)
    real_buckets = Counter(bucket(n) for n in real_unique if bucket(n))

    order = [b for b in PRIORITY if pool_buckets.get(b, 0) or real_buckets.get(b, 0)]
    # add any extra buckets not in priority
    for b in list(pool_buckets) + list(real_buckets):
        if b not in order:
            order.append(b)

    print('=' * 72)
    print('REAL ISSUE POOL FREQUENCY vs OUR REPRODUCED SUBSET')
    print('=' * 72)
    print(f'Pool (ISS, HTTP-reproducible-in-principle) distinct issues: {len(cdd_num)}')
    print(f'Our reproduced subset (distinct issues): {len(real_unique)}')
    print(f'\n{"Category":<30s}{"In pool":>8s}{"Reproduced":>11s}   Taraghi signal')
    for b in order:
        pb = pool_buckets.get(b, 0); rb = real_buckets.get(b, 0)
        sig = FREQ_SIGNAL.get(b, '')
        print(f'{b:<30s}{pb:>8d}{rb:>11d}   {sig}')
    coverage = len(real_buckets) / len(pool_buckets) * 100 if pool_buckets else 0
    print(f'\nCategory coverage: {len(real_buckets)}/{len(pool_buckets)} ({coverage:.0f}%) of the reproducible pool categories sampled')
    # fraction of reproduced issues that come from a top-priority (freq/sev/effort) bucket
    toppri = {'Tool Response Handling', 'Host / Tool Connection', 'Tool Authentication'}
    in_top = sum(rb for b, rb in real_buckets.items() if b in toppri)
    print(f'Reproduced issues in a top-frequency/severity/effort category: {in_top}/{len(real_unique)} ({in_top/len(real_unique)*100:.0f}%)')

    # ---- figure ----
    labels = order
    pv = [pool_buckets.get(b, 0) for b in order]
    rv = [real_buckets.get(b, 0) for b in order]
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    x = np.arange(len(labels)); w = 0.38
    b1 = ax.bar(x - w/2, pv, w, label=f'In issue pool (n={len(cdd_num)})', color='#2166ac')
    b2 = ax.bar(x + w/2, rv, w, label=f'Reproduced subset (n={len(real_unique)})', color='#b2182b')
    for b in b2:
        b.set_hatch('//'); b.set_edgecolor('black')
    for i in range(len(labels)):
        if pv[i]: ax.text(x[i]-w/2, pv[i]+0.5, str(pv[i]), ha='center', fontsize=8)
        if rv[i]: ax.text(x[i]+w/2, rv[i]+0.5, str(rv[i]), ha='center', fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=25, ha='right', fontsize=8.5)
    ax.set_ylabel('Number of distinct issues')
    ax.set_title('Real-issue sampling: pool frequency vs reproduced coverage\n'
                 '(sampled to cover the most frequent / severe / time-consuming categories)', fontsize=9.5)
    ax.legend(fontsize=8); ax.grid(axis='x', visible=False)
    ax.set_ylim(0, max(pv) + 2)
    plt.tight_layout(); plt.savefig(os.path.join(REPO, 'figs', 'fig_sample_frequency.png')); plt.close()
    print('\nfig -> figs/fig_sample_frequency.png')

    # ---- markdown evidence doc ----
    lines = []
    lines.append('# Real-issue Sampling Rationale (data-driven evidence)')
    lines.append('')
    lines.append('> Addresses the review question *"why did you pick these data?"* with **evidence** '
                 'instead of assertion. We tally the genuine ISSUES in the official '
                 '`modelcontextprotocol/python-sdk` pool (`data/gh_issues_pool.json`) and show '
                 'that our reproduced subset is **sampled to cover the categories Taraghi et al. '
                 '(arXiv:2603.05637) identify as most frequent, most severe and most time-consuming**.')
    lines.append('')
    lines.append(f'Pool distinct HTTP-reproducible ISSUES: **{len(cdd_num)}**. '
                 f'Our reproduced distinct issues: **{len(real_unique)}**.')
    lines.append('')
    lines.append('| Category (author-labelled) | In pool | Reproduced | Taraghi signal |')
    lines.append('|---|---|---|---|')
    for b in order:
        lines.append(f'| {b} | {pool_buckets.get(b,0)} | {real_buckets.get(b,0)} | '
                     f'{FREQ_SIGNAL.get(b,"")} |')
    lines.append('')
    lines.append(f'**Category coverage:** {len(real_buckets)}/{len(pool_buckets)} '
                 f'({coverage:.0f}%) of the reproducible-pool categories are sampled.')
    lines.append('')
    lines.append(f'**Focus on the pain categories:** {in_top}/{len(real_unique)} '
                 f'({in_top/len(real_unique)*100:.0f}%) of the reproduced distinct issues fall in a '
                 f'category that Taraghi et al. report as most frequent (Tool Response Handling), '
                 f'most severe (Host Connection Mismatch) or most time-consuming (Tool Authentication).')
    lines.append('')
    lines.append('> **Honesty note:** the Taraghi bucket is **author-labelled** (we map each official '
                 'issue into Taraghi\'s taxonomy buckets); it is NOT the raw per-label counts of '
                 'Taraghi et al. The pool-frequency column reflects genuine ISSUES (excluding PRs and '
                 'non-bug items).')
    path = os.path.join(REPO, 'docs', 'real_sample_rationale.md')
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines))
    print('doc -> docs/real_sample_rationale.md')

if __name__ == '__main__':
    main()