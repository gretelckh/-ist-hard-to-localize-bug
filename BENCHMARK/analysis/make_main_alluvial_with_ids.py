#!/usr/bin/env python3
"""
Main paper alluvial causal diagram for the 49 reproduced MCP bugs (modern, journal style).
- Left: 4 origin-layer aggregated nodes (layer label + total count)
- Beside each layer node: the issue ids of that layer printed VERTICALLY
- One thin ribbon per bug (not aggregated), coloured by origin layer, semi-transparent
- Smooth S-curve (sigmoid) connectors, muted academic palette
- Right: exposure-channel nodes + total counts
- Output vector PDF (paper) + PNG
"""
import os, json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyBboxPatch
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..'))
BASE = os.path.join(REPO, 'data', 'full_pool')
FIG = os.path.join(REPO, 'figs'); os.makedirs(FIG, exist_ok=True)
AN = os.path.join(BASE, 'active_dataset_analysis.json')

# ---- muted, academic palette (calm, low-saturation) ----
ORIGINS = [
    ("Host",      "#8c6d31"),   # muted ochre / brown
    ("Client",    "#4c72b0"),   # slate blue
    ("Server",    "#c44e52"),   # dusty rose
    ("Transport", "#55a868"),   # sage green
]
ORIG_ORDER = [o[0] for o in ORIGINS]
ORIG_COLOR = dict(ORIGINS)

# exposure channels (right column)
CHANNELS = [
    ('pushed-server',       'Pushed-to-Server'),
    ('silent',              'Silent'),
    ('caller-exception',    'Caller-exception'),
    ('single-layer-masked', 'Single-layer (genericised)'),
    ('single-layer-correct','Single-layer (correct)'),
    ('registration-error',  'Registration'),
]
CH_KEY_LIST = [c[0] for c in CHANNELS]
CH_LABEL = {c[0]: c[1] for c in CHANNELS}

ALPHA = 0.30          # ribbon transparency
RIBBON_W = 0.40       # width of a single-bug ribbon
BAR_X0 = 0.6          # left node x
BAR_X1 = 12.6         # right node x
BAR_W = 0.42          # node bar width


def sigmoid_edge(p0, p1, n=80, sharpness=9.0):
    """Smooth S-curve (sigmoid) from left point to right point with flat ends."""
    x0, y0 = p0
    x1, y1 = p1
    xs = np.linspace(x0, x1, n)
    t = (xs - x0) / (x1 - x0)
    # logistic easing: flat at both ends, smooth S in the middle
    s = 1.0 / (1.0 + np.exp(-sharpness * (t - 0.5)))
    s = (s - s.min()) / (s.max() - s.min())   # normalise to [0,1]
    ys = y0 + (y1 - y0) * s
    return list(zip(xs, ys))


def main():
    raw = json.load(open(AN, encoding='utf-8'))
    bug_list = raw['tier_b']['per_bug']

    bug_list_sorted = sorted(bug_list, key=lambda b: (ORIG_ORDER.index(b['origin']), b['issue']))

    group = defaultdict(list)
    for b in bug_list_sorted:
        group[b['origin']].append(b)

    # ---- left y positions: one bug per unit, gap between layers ----
    bug_y = {}
    gap_between_groups = 1.4
    y_cur = 0.0
    for orig, _ in ORIGINS:
        for b in group[orig]:
            bug_y[b['issue']] = y_cur
            y_cur += 1.0
        y_cur += gap_between_groups
    total_left_height = y_cur

    # ---- right y positions per channel ----
    ch_count = defaultdict(int)
    for b in bug_list_sorted:
        ch_count[b['channel']] += 1
    ch_y_offset = {}
    ry = 0.0
    for chk in CH_KEY_LIST:
        ch_y_offset[chk] = ry
        ry += ch_count[chk] + 0.8
    total_right_height = ry

    fig_h = max(total_left_height, total_right_height) * 0.24
    fig, ax = plt.subplots(figsize=(16, fig_h), dpi=150)
    ax.set_xlim(-2.4, 14.5)
    ax.set_ylim(-1, max(total_left_height, total_right_height) + 1)
    ax.axis('off')

    # ---- one thin ribbon per bug (draw first, behind nodes) ----
    ch_used = defaultdict(float)
    for b in bug_list_sorted:
        ly = bug_y[b['issue']]
        chk = b['channel']
        ry_base = ch_y_offset[chk] + ch_used[chk]
        ch_used[chk] += 1.0
        c = ORIG_COLOR[b['origin']]

        left_top = (BAR_X0 + BAR_W, ly + RIBBON_W / 2)
        left_bot = (BAR_X0 + BAR_W, ly - RIBBON_W / 2)
        right_top = (BAR_X1, ry_base + RIBBON_W / 2)
        right_bot = (BAR_X1, ry_base - RIBBON_W / 2)

        top_curve = sigmoid_edge(left_top, right_top)
        bot_curve = sigmoid_edge(left_bot, right_bot)
        poly_pts = top_curve + list(reversed(bot_curve))
        poly = Polygon(poly_pts, facecolor=c, alpha=ALPHA,
                       edgecolor='none', linewidth=0, zorder=1)
        ax.add_patch(poly)

    # ---- left layer nodes (rounded bar) + label + count ----
    for orig, _ in ORIGINS:
        bugs = group[orig]
        top = bug_y[bugs[0]['issue']] + 0.55
        bot = bug_y[bugs[-1]['issue']] - 0.55
        ax.add_patch(FancyBboxPatch((BAR_X0, bot), BAR_W, top - bot,
                                    boxstyle='round,pad=0.02,rounding_size=0.06',
                                    facecolor=ORIG_COLOR[orig], edgecolor='none',
                                    alpha=0.95, zorder=2))
        mid = (top + bot) / 2
        ax.text(BAR_X0 + BAR_W + 0.18, mid,
                f"{orig}  ({len(bugs)})", ha='left', va='center',
                fontsize=11.5, weight='bold', color=ORIG_COLOR[orig], zorder=3)

        # issue ids VERTICALLY, centred on the group, to the left of the bar
        ids = [str(b['issue']) for b in bugs]
        for j, iid in enumerate(ids):
            line_y = mid - (len(ids) - 1) / 2.0 + j
            ax.text(BAR_X0 - 0.28, line_y, iid, ha='right', va='center',
                    fontsize=6.5, color='#333333', zorder=3)

    # ---- right channel nodes (grey rounded bar) + label + count ----
    for chk in CH_KEY_LIST:
        cnt = ch_count[chk]
        base = ch_y_offset[chk]
        top = base + cnt - 0.55
        bot = base - 0.55
        ax.add_patch(FancyBboxPatch((BAR_X1, bot), BAR_W, top - bot,
                                    boxstyle='round,pad=0.02,rounding_size=0.06',
                                    facecolor='#9aa0a6', edgecolor='none',
                                    alpha=0.9, zorder=2))
        mid = (top + bot) / 2
        ax.text(BAR_X1 + BAR_W + 0.18, mid,
                f"{CH_LABEL[chk]}  ({cnt})", ha='left', va='center',
                fontsize=9.5, weight='bold', color='#404040', zorder=3)

    ax.set_title('49 reproduced MCP bugs: origin layer to exposure channel',
                 fontsize=13, pad=12, color='#1a1a1a')
    plt.tight_layout()
    fig.savefig(os.path.join(FIG, 'fig_main_alluvial_with_ids.pdf'), bbox_inches='tight')
    fig.savefig(os.path.join(FIG, 'fig_main_alluvial_with_ids.png'), dpi=300, bbox_inches='tight')
    print('Saved modern alluvial: smooth S-curve ribbons, muted palette, vertical ids.')


if __name__ == '__main__':
    main()