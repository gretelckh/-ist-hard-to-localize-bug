#!/usr/bin/env python3
"""Draw an alluvial / sankey diagram: origin LAYER -> ROOT-CAUSE category for the
49 reproduced MCP bugs.

The three-channel exposure model describes HOW the SDK exposes a fault, not WHY it
exists. This figure flows each bug from its origin layer to its root-cause category
so the paper can clearly state that layer is a *classification dimension*.

Uses plotly go.Sankey (interactive HTML) and exports a static PNG for the paper.

Data source: data/full_pool/rootcause_49.json (issue -> origin, root_cause)

Outputs (into <repo>/figs/):
  - fig_rootcause_sankey.html   interactive (plotly)
  - fig_rootcause_sankey.png    static (for the paper)

Run from MCP-Fault-Benchmark/:
    python analysis/make_rootcause_sankey.py
"""
import os, json, sys
sys.stdout.reconfigure(encoding='utf-8')
import plotly.graph_objects as go
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..'))
BASE = os.path.join(REPO, 'data', 'full_pool')
FIG = os.path.join(REPO, 'figs'); os.makedirs(FIG, exist_ok=True)
RC = os.path.join(BASE, 'rootcause_49.json')

# origin layer colours
ORIGINS = [('Host', '#d95f02'), ('Client', '#377eb8'),
           ('Server', '#f781bf'), ('Transport', '#4daf4a')]


def main():
    rc = json.load(open(RC, encoding='utf-8'))
    items = rc['items']
    cat_label = rc['categories']
    cat_color = rc['colors']
    links = Counter((b['origin'], b['root_cause']) for b in items)

    origin_color = dict(ORIGINS)
    cats = list(cat_label.keys())

    nodes = [o for o, _ in ORIGINS] + [cat_label[c] for c in cats]
    n_orig = len(ORIGINS)
    colors = [origin_color[o] for o, _ in ORIGINS] + [cat_color[c] for c in cats]

    source, target, value, link_color = [], [], [], []
    origin_idx = {o: i for i, (o, _) in enumerate(ORIGINS)}
    cat_idx = {c: i for i, c in enumerate(cats)}
    for (o, c), v in links.items():
        source.append(origin_idx[o])
        target.append(n_orig + cat_idx[c])
        value.append(v)
        link_color.append(cat_color[c])

    fig = go.Figure(go.Sankey(
        arrangement='snap',
        node=dict(
            label=nodes, color=colors, pad=18, thickness=22,
            line=dict(color='white', width=1),
        ),
        link=dict(source=source, target=target, value=value, color=link_color,
                  line=dict(color='white', width=0.5)),
    ))
    fig.update_layout(
        title=dict(text='Root cause of 49 reproduced MCP bugs: '
                        'origin layer to root-cause category', x=0.5, font=dict(size=14)),
        font=dict(size=13, color='black'),
        plot_bgcolor='white', paper_bgcolor='white',
        width=900, height=650, margin=dict(l=20, r=20, t=60, b=20),
    )

    html = os.path.join(FIG, 'fig_rootcause_sankey.html')
    fig.write_html(html)
    png = os.path.join(FIG, 'fig_rootcause_sankey.png')
    fig.write_image(png, scale=2.5)
    print('->', html)
    print('->', png)


if __name__ == '__main__':
    main()