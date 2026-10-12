#!/usr/bin/env python3
"""Draw the three-channel exposure model of the 49 reproduced bugs as a
Sankey / alluvial diagram (origin layer -> exposure channel).

Uses plotly go.Sankey (interactive HTML) and exports a static PNG for the paper.

Data source: data/full_pool/active_dataset_analysis.json -> tier_b.per_bug

Outputs (into <repo>/figs/):
  - fig_exposure_sankey.html   interactive (plotly)
  - fig_exposure_sankey.png    static (for the paper)

Run from MCP-Fault-Benchmark/:
    python analysis/make_exposure_sankey.py
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

# origin layer -> exposure channel colouring
CHANNELS = [
    ('pushed-server',       'Pushed-to-Server',    '#7570b3'),
    ('silent',              'Silent',              '#e41a1c'),
    ('caller-exception',    'Caller-exception',    '#1b9e77'),
    ('single-layer-masked', 'Single-layer (genericised)', '#e6a817'),
    ('single-layer-correct','Single-layer (correct)', '#4daf4a'),
    ('registration-error',  'Registration',        '#999999'),
]
ORIGINS = [('Host', '#d95f02'), ('Client', '#377eb8'),
           ('Server', '#f781bf'), ('Transport', '#4daf4a')]


def main():
    an = json.load(open(AN, encoding='utf-8'))
    per = an['tier_b']['per_bug']
    links = Counter((b['origin'], b['channel']) for b in per)

    ch_key = [c[0] for c in CHANNELS]
    ch_label = {c[0]: c[1] for c in CHANNELS}
    ch_color = {c[0]: c[2] for c in CHANNELS}
    origin_color = dict(ORIGINS)

    # node list: origins first (0..3), then channels (4..9)
    nodes = [o for o, _ in ORIGINS] + [ch_label[c] for c in ch_key]
    n_orig = len(ORIGINS)
    colors = [origin_color[o] for o, _ in ORIGINS] + [ch_color[c] for c in ch_key]

    source, target, value, link_color = [], [], [], []
    origin_idx = {o: i for i, (o, _) in enumerate(ORIGINS)}
    ch_idx = {c: i for i, c in enumerate(ch_key)}
    for (o, ch), v in links.items():
        source.append(origin_idx[o])
        target.append(n_orig + ch_idx[ch])
        value.append(v)
        link_color.append(ch_color[ch])

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
        title=dict(text='Three-channel exposure of 49 reproduced MCP bugs: '
                        'origin layer to exposure channel', x=0.5, font=dict(size=14)),
        font=dict(size=13, color='black'),
        plot_bgcolor='white', paper_bgcolor='white',
        width=900, height=650, margin=dict(l=20, r=20, t=60, b=20),
    )

    html = os.path.join(FIG, 'fig_exposure_sankey.html')
    fig.write_html(html)
    png = os.path.join(FIG, 'fig_exposure_sankey.png')
    fig.write_image(png, scale=2.5)
    print('->', html)
    print('->', png)


if __name__ == '__main__':
    main()