#!/usr/bin/env python3
"""Alluvial / sankey: the 49 reproduced bugs (left, one node each, grouped & coloured
by origin LAYER) flow to the exposure channel they were observed through (right).

Each bug on the left is a single node labelled by its issue id. Bugs of the same
origin layer are grouped together (same starting point) and share the layer colour.
Each bug flows to its exposure channel (pushed-server / silent / caller-exception /
single-layer-masked / single-layer-correct / registration-error).

Uses plotly go.Sankey (interactive HTML) and exports a static PNG for the paper.

Data source: data/full_pool/active_dataset_analysis.json -> tier_b.per_bug

Outputs (into <repo>/figs/):
  - fig_bug_channel_sankey.html   interactive (plotly)
  - fig_bug_channel_sankey.png    static (for the paper)

Run from MCP-Fault-Benchmark/:
    python analysis/make_bug_channel_sankey.py
"""
import os, json, sys
sys.stdout.reconfigure(encoding='utf-8')
import plotly.graph_objects as go
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..'))
BASE = os.path.join(REPO, 'data', 'full_pool')
FIG = os.path.join(REPO, 'figs'); os.makedirs(FIG, exist_ok=True)
AN = os.path.join(BASE, 'active_dataset_analysis.json')

# origin layer colours
ORIGINS = [('Host', '#d95f02'), ('Client', '#377eb8'),
           ('Server', '#f781bf'), ('Transport', '#4daf4a')]

# exposure channels (right column)
CHANNELS = [
    ('pushed-server',       'Pushed-to-Server',    '#7570b3'),
    ('silent',              'Silent',              '#e41a1c'),
    ('caller-exception',    'Caller-exception',    '#1b9e77'),
    ('single-layer-masked', 'Single-layer (genericised)', '#e6a817'),
    ('single-layer-correct','Single-layer (correct)', '#4daf4a'),
    ('registration-error',  'Registration',        '#999999'),
]


def main():
    an = json.load(open(AN, encoding='utf-8'))
    per = an['tier_b']['per_bug']

    origin_color = dict(ORIGINS)
    ch_key = [c[0] for c in CHANNELS]
    ch_label = {c[0]: c[1] for c in CHANNELS}
    ch_color = {c[0]: c[2] for c in CHANNELS}

    # order origin layers as in ORIGINS
    layer_order = [o for o, _ in ORIGINS]
    per_sorted = sorted(per, key=lambda b: (layer_order.index(b['origin']), b['issue']))

    # left nodes = one per bug, label = issue id, colour = layer colour
    bug_nodes = [(b['issue'], b['origin']) for b in per_sorted]
    node_labels = [str(i) for i, _ in bug_nodes]
    node_colors = [origin_color[o] for _, o in bug_nodes]

    # right nodes = channels
    ch_nodes = [ch_label[c] for c in ch_key]
    n_bug = len(bug_nodes)
    n_orig = len(ORIGINS)

    nodes = node_labels + ch_nodes
    colors = node_colors + [ch_color[c] for c in ch_key]

    source, target, value, link_color = [], [], [], []
    bug_idx = {i: k for k, (i, _) in enumerate(bug_nodes)}
    ch_idx = {c: k for k, c in enumerate(ch_key)}
    for b in per_sorted:
        source.append(bug_idx[b['issue']])
        target.append(n_bug + ch_idx[b['channel']])
        value.append(1)
        link_color.append(origin_color[b['origin']])

    # fixed layout: left bug nodes grouped by origin layer (same x, y within group),
    # right channel nodes on the far right
    x = [0.0] * n_bug
    y = [0.0] * n_bug
    group_pos = {o: k for k, (o, _) in enumerate(ORIGINS)}
    group_counts = Counter(o for _, o in bug_nodes)
    group_index = Counter()
    for k, (i, o) in enumerate(bug_nodes):
        g = group_pos[o]
        # split each group into its own vertical band; within a band spread evenly
        top = 1.0 - (g + 1) * (1.0 / (n_orig + 1))
        band_h = 1.0 / (n_orig + 1)
        n_in = group_counts[o]
        j = group_index[o]; group_index[o] += 1
        y[k] = top - (j + 0.5) * (band_h / n_in)

    ch_x = [1.0] * len(ch_nodes)
    ch_y = [(1.0 - (k + 0.5) / len(ch_nodes)) for k in range(len(ch_nodes))]
    node_x = x + ch_x
    node_y = y + ch_y

    fig = go.Figure(go.Sankey(
        arrangement='fixed',
        node=dict(
            label=nodes, color=colors, pad=12, thickness=22,
            line=dict(color='white', width=1),
            x=node_x, y=node_y,
        ),
        link=dict(source=source, target=target, value=value, color=link_color,
                  line=dict(color='white', width=0.5)),
    ))
    fig.update_layout(
        title=dict(text='49 reproduced MCP bugs (coloured by origin layer) '
                        'to exposure channel', x=0.5, font=dict(size=14)),
        font=dict(size=12, color='black'),
        plot_bgcolor='white', paper_bgcolor='white',
        width=1100, height=900, margin=dict(l=40, r=40, t=60, b=20),
    )

    html = os.path.join(FIG, 'fig_bug_channel_sankey.html')
    fig.write_html(html)
    png = os.path.join(FIG, 'fig_bug_channel_sankey.png')
    fig.write_image(png, scale=2.5)
    print('->', html)
    print('->', png)


if __name__ == '__main__':
    main()