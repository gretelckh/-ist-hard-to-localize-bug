#!/usr/bin/env python3
"""Generate the five paper figures referenced by the submission (main_review/05_results.tex)
from the AUTHORITATIVE 49-bug real-bug data, replacing the old 80-run synthetic versions.

Figures produced (written to <repo>/figs/ AND paper/figs/):
  - fig_layer_distribution.png   origin layer x exposure channel of the 49 reproduced bugs
  - fig_causal_graph.png         three-channel exposure of the 13 non-Server bugs (origin -> channel)
  - fig_silent_failure.png       the 11 silent bugs, by origin layer
  - fig_diag_clues.png           baseline vs +honest clue vs +leaky label (overall & non-Server)
  - fig_topk.png                 Top-K localisation (overall vs non-Server)

Data sources (all authoritative, 49-bug scope):
  - data/full_pool/active_dataset_analysis.json  -> tier_b (channels, per_bug, by_origin)
  - data/full_pool/topk_49.json                  -> Top-K hit rates
  - data/full_pool/clues_49_summary.json         -> clue-intervention comparison

Usage:
    python analysis/make_49_figs.py
"""
import os, sys, json
sys.stdout.reconfigure(encoding='utf-8')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from collections import Counter, defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, 'data', 'full_pool')
OUT = os.path.join(REPO, 'figs')
os.makedirs(OUT, exist_ok=True)
# also mirror into the paper/figs dir used by the submission build
PAPER_FIGS = os.path.normpath(os.path.join(REPO, '..', 'paper', 'figs'))

ds = json.load(open(os.path.join(DATA, 'active_dataset_analysis.json'), encoding='utf-8'))
tb = ds['tier_b']
pb = tb['per_bug']
topk = json.load(open(os.path.join(DATA, 'topk_49.json'), encoding='utf-8'))
clues = json.load(open(os.path.join(DATA, 'clues_49_summary.json'), encoding='utf-8'))

CH_COLOR = {
    'pushed-server': '#7570b3',
    'caller-exception': '#1b9e77',
    'silent': '#e41a1c',
    'single-layer-masked': '#d95f02',
    'single-layer-correct': '#66a61e',
    'registration-error': '#e6ab02',
}
CH_LABEL = {
    'pushed-server': 'Pushed to Server',
    'caller-exception': 'Caller exception',
    'silent': 'Silent (hidden)',
    'single-layer-masked': 'Single layer, genericised',
    'single-layer-correct': 'Single layer, correct',
    'registration-error': 'Registration error',
}

LAYERS = ['Host', 'Client', 'Server', 'Transport']


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=200, bbox_inches='tight')
    fig.savefig(os.path.join(PAPER_FIGS, name), dpi=200, bbox_inches='tight')
    plt.close(fig)
    print('wrote', name)


# ---- Fig 1: layer distribution (49 bugs, origin layer x exposure) ----
def fig_layer_distribution():
    by_origin = {L: Counter() for L in LAYERS}
    for p in pb:
        by_origin[p['origin']][p['channel']] += 1
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    x = np.arange(4)
    # stack order: pushed, caller, silent, registration, single-masked, single-correct
    order = ['pushed-server', 'caller-exception', 'silent',
             'registration-error', 'single-layer-masked', 'single-layer-correct']
    bottom = np.zeros(4)
    for ch in order:
        vals = np.array([by_origin[L][ch] for L in LAYERS])
        ax.bar(x, vals, bottom=bottom, label=CH_LABEL[ch], color=CH_COLOR[ch], edgecolor='white', linewidth=0.4)
        for i in range(4):
            if vals[i]:
                ax.text(i, bottom[i] + vals[i] / 2, str(vals[i]), ha='center', va='center',
                        color='white', fontsize=9)
        bottom += vals
    for i, L in enumerate(LAYERS):
        ax.text(i, bottom[i] + 0.4, str(int(bottom[i])), ha='center', fontsize=10, weight='bold')
    ax.set_xticks(x); ax.set_xticklabels(LAYERS)
    ax.set_ylabel('Reproduced bugs'); ax.set_ylim(0, bottom.max() + 5)
    ax.set_title('Origin layer and exposure channel of the 49 reproduced real bugs', fontsize=10)
    ax.legend(loc='upper right', fontsize=7, framealpha=0.9)
    ax.grid(axis='y', alpha=0.25)
    save(fig, 'fig_layer_distribution.png')


# ---- Fig 2: causal / three-channel exposure of the 13 non-Server bugs ----
def fig_causal_graph():
    non = [p for p in pb if p['origin'] != 'Server']
    flow = defaultdict(Counter)   # origin -> channel
    for p in non:
        flow[p['origin']][p['channel']] += 1
    origins = ['Host', 'Client', 'Transport']
    chs = ['pushed-server', 'caller-exception', 'silent']
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    L = 0.20; M = 0.80
    ypos = {'Host': 0.83, 'Client': 0.5, 'Transport': 0.17}
    chan_y = {'pushed-server': 0.83, 'silent': 0.5, 'caller-exception': 0.17}
    for o in origins:
        y0 = ypos[o]
        for ch in chs:
            v = flow[o][ch]
            if v == 0:
                continue
            xs = np.linspace(L, M, 50)
            yt = np.linspace(y0 + 0.04, chan_y[ch] + 0.04, 50)
            yb = np.linspace(y0 - 0.04, chan_y[ch] - 0.04, 50)
            ax.fill_between(xs, yb, yt, color=CH_COLOR[ch], alpha=0.35, edgecolor='none')
        tot = sum(flow[o].values())
        ax.text(L - 0.02, y0, f'{o}-origin\n({tot} bugs)', ha='right', va='center',
                fontsize=10, weight='bold')
    right_counts = {ch: sum(flow[o][ch] for o in origins) for ch in chs}
    for ch in chs:
        ax.text(M + 0.02, chan_y[ch], f'{CH_LABEL[ch]}\n({right_counts[ch]})',
                ha='left', va='center', fontsize=9, weight='bold', color=CH_COLOR[ch])
    for o in origins:
        ax.add_patch(mpatches.Circle((L, ypos[o]), 0.09, color='#333333', zorder=5))
    for ch in chs:
        ax.add_patch(mpatches.Circle((M, chan_y[ch]), 0.09, color=CH_COLOR[ch], zorder=5))
    ax.set_xlim(-0.05, 1.30); ax.set_ylim(0, 1.0); ax.axis('off')
    ns = len(non)
    ax.set_title(f'Where non-Server MCP bugs originate (left) vs where they are exposed (right)\n'
                 f'all {ns}/{ns} non-Server bugs are not localised at their true origin '
                 f'({tb["mismatch_count"]}/{ns} = {tb["mismatch_rate"]*100:.1f}% mismatched)',
                 fontsize=10.5)
    handles = [mpatches.Patch(color=CH_COLOR[ch], label=CH_LABEL[ch]) for ch in chs]
    ax.legend(handles=handles, loc='lower center', bbox_to_anchor=(0.5, -0.04), ncol=3, fontsize=8)
    save(fig, 'fig_causal_graph.png')


# ---- Fig 3: the silent bugs (11/49), by origin layer ----
def fig_silent_failure():
    silent = [p for p in pb if p['channel'] == 'silent']
    by_origin = Counter(p['origin'] for p in silent)
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    layers = [L for L in LAYERS if by_origin[L]]
    vals = [by_origin[L] for L in layers]
    bars = ax.bar(layers, vals, color='#e41a1c', edgecolor='black', linewidth=0.5)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.12, str(v), ha='center', fontsize=10, weight='bold')
    ax.set_ylabel('Silent bugs'); ax.set_ylim(0, max(vals) + 1.2)
    ax.set_title(f'Silent failures among the 49 reproduced real bugs\n'
                 f'{tb["silent_count"]}/{len(pb)} = {tb["silent_rate"]*100:.1f}% '
                 f'({", ".join(layers)})', fontsize=10)
    ax.grid(axis='y', alpha=0.25)
    save(fig, 'fig_silent_failure.png')


# ---- Fig 4: diagnosis baseline vs +clue vs +leaky label ----
def fig_diag_clues():
    conds = ['baseline', 'honest_clue', 'leaky_label']
    labels = ['Baseline\n(no clue)', '+ Honest clue', '+ Leaky label\n(control)']
    overall = [clues[c]['overall'] for c in conds]
    nonserver = [clues[c]['nonserver'] for c in conds]
    x = np.arange(3); w = 0.35
    fig, ax = plt.subplots(figsize=(7.0, 4.4))
    b1 = ax.bar(x - w / 2, overall, w, label='Overall (49 bugs)', color='#4d4d4d')
    b2 = ax.bar(x + w / 2, nonserver, w, label='Non-Server (13 bugs)', color='#e41a1c')
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.8,
                    f'{b.get_height():.1f}%', ha='center', fontsize=9, weight='bold')
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel('Root-cause localisation accuracy (%)'); ax.set_ylim(0, 100)
    ax.set_title('Diagnostic-clue intervention over the 49 reproduced real bugs', fontsize=10)
    ax.legend(loc='upper right', fontsize=8); ax.grid(axis='y', alpha=0.25)
    save(fig, 'fig_diag_clues.png')


# ---- Fig 5: Top-K localisation ----
def fig_topk():
    ks = [1, 2, 3]
    allk = [topk['all'][str(k)][2] for k in ks]
    nsk = [topk['nonserver'][str(k)][2] for k in ks]
    x = np.arange(3)
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.plot(x, allk, 'o-', color='#4d4d4d', label='Overall (49 bugs)', linewidth=2, markersize=7)
    ax.plot(x, nsk, 's-', color='#e41a1c', label='Non-Server (13 bugs)', linewidth=2, markersize=7)
    for i in range(3):
        ax.annotate(f'{allk[i]:.1f}%', (x[i], allk[i]), textcoords='offset points',
                    xytext=(0, 8), ha='center', fontsize=9, color='#4d4d4d')
        ax.annotate(f'{nsk[i]:.1f}%', (x[i], nsk[i]), textcoords='offset points',
                    xytext=(0, -14), ha='center', fontsize=9, color='#e41a1c')
    ax.set_xticks(x); ax.set_xticklabels(['Top-1', 'Top-2', 'Top-3'])
    ax.set_ylabel('Localisation hit rate (%)'); ax.set_ylim(0, 105)
    ax.set_title('Top-K root-cause localisation from surface text (49 reproduced bugs)', fontsize=10)
    ax.legend(loc='lower right', fontsize=8); ax.grid(alpha=0.25)
    save(fig, 'fig_topk.png')


if __name__ == '__main__':
    fig_layer_distribution()
    fig_causal_graph()
    fig_silent_failure()
    fig_diag_clues()
    fig_topk()
    print('All 5 figures written to', OUT, 'and', PAPER_FIGS)