#!/usr/bin/env python3
"""
Causal-style alluvial diagram
- Left side: every bug has its own label (issue id), grouped vertically by origin layer
- One flow per bug, flow colour matches its origin layer
- Right side: exposure-channel nodes
- Output vector PDF for paper + PNG
"""
import os, json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..'))
BASE = os.path.join(REPO, 'data', 'full_pool')
FIG = os.path.join(REPO, 'figs')
os.makedirs(FIG, exist_ok=True)
AN = os.path.join(BASE, 'active_dataset_analysis.json')

# origin layer style
ORIGINS = [
    ("Host", "#d95f02"),
    ("Client", "#377eb8"),
    ("Server", "#f781bf"),
    ("Transport", "#4daf4a"),
]
ORIG_ORDER = [o[0] for o in ORIGINS]
ORIG_COLOR = dict(ORIGINS)

# exposure channels mapping
CHANNELS = [
    ('pushed-server',       'Pushed-to-Server'),
    ('silent',              'Silent'),
    ('caller-exception',    'Caller-exception'),
    ('single-layer-masked', 'Single-layer (genericised)'),
    ('single-layer-correct','Single-layer (correct)'),
    ('registration-error',  'Registration'),
]
CH_KEY_LIST = [c[0] for c in CHANNELS]
CH_LABEL_DICT = {c[0]: c[1] for c in CHANNELS}

def spline_quad(p0, p1, p2, n=30):
    """quadratic bezier spline for alluvial ribbon edges"""
    pts = []
    for t in [i/(n-1) for i in range(n)]:
        x = (1-t)**2 * p0[0] + 2*(1-t)*t*p1[0] + t**2 * p2[0]
        y = (1-t)**2 * p0[1] + 2*(1-t)*t*p1[1] + t**2 * p2[1]
        pts.append((x,y))
    return pts

def main():
    raw = json.load(open(AN, encoding="utf-8"))
    bug_list = raw["tier_b"]["per_bug"]
    # sort: group by origin layer
    bug_list_sorted = sorted(bug_list, key=lambda b: ORIG_ORDER.index(b["origin"]))

    # group bugs by origin
    from collections import defaultdict
    group = defaultdict(list)
    for b in bug_list_sorted:
        group[b["origin"]].append(b)

    # assign y-position for each bug on left side
    bug_y = dict()
    gap_between_groups = 0.8
    y_cur = 0.0
    for orig,_ in ORIGINS:
        bugs_in_group = group[orig]
        for b in bugs_in_group:
            bug_y[b["issue"]] = y_cur
            y_cur += 1.0
        y_cur += gap_between_groups

    total_left_height = y_cur

    # assign y-position for each channel on right side
    ch_count = defaultdict(int)
    for b in bug_list_sorted:
        ch_count[b["channel"]] += 1
    ch_y_offset = dict()
    ry = 0.0
    for chk in CH_KEY_LIST:
        cnt = ch_count[chk]
        ch_y_offset[chk] = ry
        ry += cnt + 0.6
    total_right_height = ry

    fig_height = max(total_left_height, total_right_height) * 0.22
    fig, ax = plt.subplots(figsize=(14, fig_height), dpi=150)
    ax.set_xlim(-2, 14)
    ax.set_ylim(-1, max(total_left_height, total_right_height)+1)
    ax.axis("off")

    # draw left labels: every bug issue id
    for orig,_ in ORIGINS:
        for b in group[orig]:
            y = bug_y[b["issue"]]
            ax.text(0.2, y, str(b["issue"]), ha="right", va="center", fontsize=7.5)

    # draw right-side channel labels & accumulate used y for each channel
    ch_used_y = defaultdict(float)
    for chk in CH_KEY_LIST:
        lab = CH_LABEL_DICT[chk]
        base_y = ch_y_offset[chk]
        ax.text(13.2, base_y + ch_count[chk]/2.0, lab, ha="left", va="center", fontsize=8.5)

    # draw one ribbon per bug
    for b in bug_list_sorted:
        ly = bug_y[b["issue"]]
        chk = b["channel"]
        ry_base = ch_y_offset[chk] + ch_used_y[chk]
        ch_used_y[chk] += 1.0
        c = ORIG_COLOR[b["origin"]]
        lw = 0.35
        rw = 0.35

        left_top  = (0.4, ly + lw/2)
        left_bot  = (0.4, ly - lw/2)
        right_top = (12.8, ry_base + rw/2)
        right_bot = (12.8, ry_base - rw/2)
        ctrl = (6.5, (ly+ry_base)/2)

        top_curve = spline_quad(left_top, ctrl, right_top)
        bot_curve = spline_quad(left_bot, ctrl, right_bot)
        poly_pts = top_curve + list(reversed(bot_curve))
        poly = Polygon(poly_pts, facecolor=c, alpha=0.52, edgecolor="white", linewidth=0.25)
        ax.add_patch(poly)

    fig.suptitle("49 reproduced MCP bugs: issue id (left) → exposure channel (right)", fontsize=10)
    plt.tight_layout()
    fig.savefig(os.path.join(FIG, "fig_causal_alluvial_bugs.pdf"), bbox_inches="tight")
    fig.savefig(os.path.join(FIG, "fig_causal_alluvial_bugs.png"), bbox_inches="tight")
    print("Saved causal-style alluvial with every issue id on left")

if __name__ == "__main__":
    main()