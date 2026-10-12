#!/usr/bin/env python3
"""Draw the 49-bug three-channel exposure figure and the 342-bug layer-distribution
figure as 3D bar charts (matplotlib mpl_toolkits.mplot3d).

Data source: data/full_pool/active_dataset_analysis.json + origin_labels/repro_progress.

Outputs (into <repo>/figs/):
  - fig_exposure_channels_3d.png   three-channel exposure (non-Server origins)
  - fig_layer_distribution_3d.png  layer distribution x reproduction status (342)

Run from MCP-Fault-Benchmark/:
    python analysis/make_3d_figs.py
"""
import os, json, sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..'))
BASE = os.path.join(REPO, 'data', 'full_pool')
FIG = os.path.join(REPO, 'figs'); os.makedirs(FIG, exist_ok=True)
AN = os.path.join(BASE, 'active_dataset_analysis.json')
plt.rcParams.update({'font.size': 10, 'figure.dpi': 200})


def _bar3d(ax, xpos, ypos, dz, dx=0.6, dy=0.6, color='#377eb8', edgecolor='black'):
    """Draw a 3D bar with base at (xpos, ypos), height dz, and add value labels."""
    xpos = np.asarray(xpos, dtype=float)
    ypos = np.asarray(ypos, dtype=float)
    dz = np.asarray(dz, dtype=float)
    ax.bar3d(xpos, ypos, np.zeros_like(dz), dx, dy, dz, shade=True, color=color,
             edgecolor=edgecolor, linewidth=0.4, alpha=0.92)
    for xi, yi, zi in zip(xpos, ypos, dz):
        if zi > 0:
            ax.text(xi + dx / 2, yi + dy / 2, zi + 0.3, f'{int(zi)}', ha='center',
                    va='bottom', fontsize=9, weight='bold', color='black')


def fig_exposure_3d(an):
    """Three-channel exposure model over the 13 non-Server reproduced bugs."""
    b = an['tier_b']
    origins = ['Host', 'Client', 'Transport']
    channels = [('pushed', 'Pushed-to-Server', '#7570b3'),
                ('silent', 'Silent', '#e41a1c'),
                ('caller', 'Caller-exception', '#1b9e77')]
    by = b['by_origin']

    fig = plt.figure(figsize=(9, 6.2))
    ax = fig.add_subplot(111, projection='3d')
    x = np.arange(len(origins))
    y = np.arange(len(channels))

    for yi, (key, label, color) in enumerate(channels):
        dz = [by[o].get(key, 0) for o in origins]
        xs = x - 0.3
        ys = np.full(len(origins), yi) - 0.3
        _bar3d(ax, xs, ys, np.array(dz, dtype=float), color=color)

    ax.set_xticks(x)
    ax.set_xticklabels([o + '-origin' for o in origins], fontsize=10)
    ax.set_yticks(y)
    ax.set_yticklabels([c[1] for c in channels], fontsize=9)
    ax.set_zlabel('Reproduced bugs', fontsize=10)
    ax.set_title('Three-channel exposure of non-Server MCP bugs (13 reproduced)',
                 fontsize=11, pad=12)
    ax.view_init(elev=22, azim=-58)
    ax.set_zlim(0, max(max(by[o].get('pushed', 0), by[o].get('silent', 0),
                          by[o].get('caller', 0)) for o in origins) + 3)
    # a light legend
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=c, label=l) for _, l, c in channels],
              loc='upper left', fontsize=9, frameon=True)
    ax.grid(True, alpha=0.3)
    fig.subplots_adjust(left=0.06, right=0.92, top=0.92, bottom=0.08)
    out = os.path.join(FIG, 'fig_exposure_channels_3d.png')
    plt.savefig(out); plt.close()
    print('->', out)


def fig_layer_3d(an):
    """Layer distribution x reproduction status over the 342 active dataset."""
    from collections import defaultdict
    BASE = os.path.join(REPO, 'data', 'full_pool')
    orig = json.load(open(os.path.join(BASE, 'origin_labels.json'), encoding='utf-8'))
    prog = json.load(open(os.path.join(REPO, 'data', 'repro_progress.json'), encoding='utf-8'))
    fixed = set(json.load(open(os.path.join(BASE, 'fixed_removed.json'), encoding='utf-8'))['removed_issues'])
    active = [r for r in orig if r['number'] not in fixed]
    m = defaultdict(lambda: defaultdict(int))
    for r in active:
        st = prog.get(str(r['number']), {}).get('status')
        cat = 'reproduced' if st == 'done' else ('limited' if st == 'limited' else 'auth-skip')
        m[r['origin']][cat] += 1

    layers = ['Host', 'Client', 'Server', 'Transport']
    cats = [('reproduced', 'Reproduced', '#4daf4a'),
            ('limited', 'Not-reproducible', '#ff7f00'),
            ('auth-skip', 'Auth-skip', '#999999')]

    fig = plt.figure(figsize=(9.5, 6.4))
    ax = fig.add_subplot(111, projection='3d')
    x = np.arange(len(layers))
    for yi, (key, label, color) in enumerate(cats):
        dz = [m[l].get(key, 0) for l in layers]
        _bar3d(ax, x - 0.33, np.full(len(layers), yi) - 0.33, np.array(dz, dtype=float), color=color)

    ax.set_xticks(x)
    ax.set_xticklabels([l + '-origin' for l in layers], fontsize=10)
    ax.set_yticks(np.arange(len(cats)))
    ax.set_yticklabels([c[1] for c in cats], fontsize=9)
    ax.set_zlabel('Bugs', fontsize=10)
    ax.set_title('Active bug dataset by origin layer and reproduction status (n=342)',
                 fontsize=11, pad=12)
    ax.view_init(elev=24, azim=-56)
    zmax = max(m[l].get('reproduced', 0) + m[l].get('limited', 0) + m[l].get('auth-skip', 0)
               for l in layers)
    ax.set_zlim(0, zmax + 10)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=c, label=l) for _, l, c in cats],
              loc='upper left', fontsize=9, frameon=True)
    ax.grid(True, alpha=0.3)
    fig.subplots_adjust(left=0.06, right=0.92, top=0.92, bottom=0.08)
    out = os.path.join(FIG, 'fig_layer_distribution_3d.png')
    plt.savefig(out); plt.close()
    print('->', out)


def main():
    an = json.load(open(AN, encoding='utf-8'))
    fig_exposure_3d(an)
    fig_layer_3d(an)
    print('done')


if __name__ == '__main__':
    main()