#!/usr/bin/env python3
"""Analyze the ACTIVE (342) bug dataset on top of the new MCP-Fault-Benchmark.

TWO-TIER design (honest about what can be computed from what evidence):

  TIER A - descriptive statistics on the full ACTIVE dataset (n=342):
      These need NO runtime reproduction, only the issue metadata:
        - screening funnel (1343 -> 439 -> 398 -> 342)
        - four-layer origin distribution (Server/Client/Transport/Host)
        - open/closed state
        - reproduction status split (reproduced / limited / auth-skipped)
        - WHY-bugs-cannot-be-reproduced category counts (the 'hard to localise'
          evidence, e.g. auth / env / SSE-stdio / spec-gap / concurrency)

  TIER B - three-channel exposure model on the REPRODUCED subset (n=49):
      These have real runtime evidence (data/real_raw/*.txt + repro_progress
      'message'). We classify HOW each bug is actually exposed by the MCP SDK:
        1. PUSHED-TO-SERVER  : origin != Server, but surfaced as `Error
                               executing tool X` (is_error=True) at the Server
                               tool-dispatch layer  (layer mismatch).
        2. SILENT            : is_error=False; a logical error is hidden
                               (no error flag raised).
        3. CALLER-EXCEPTION  : raw Python / HTTP exception in the calling code
                               (Transport faults, ExceptionGroup, HTTP 400/404).
      For Server-origin bugs that surface at Server, we separate:
        - single-layer-correct  : correctly reported at origin layer
        - single-layer-masked   : correctly at origin layer BUT the real error
                                  value/root-cause is genericised away
                                  (`Error executing tool X`).
        - registration-error    : server fails to build / register a tool.

      Crucially, channel/ mismatch stats are ONLY reported over n=49 (the subset
      with evidence). We never fabricate an exposure channel for a bug we did
      not observe.

Outputs:
  - data/full_pool/active_dataset_analysis.json   (all derived numbers)
  - figs/fig_funnel.png                            (screening funnel, 342)
  - figs/fig_exposure_channels.png                 (three-channel over 49)
  - figs/fig_repro_reasons.png                     (why-not-reproducible, 342)

Run from MCP-Fault-Benchmark/:
    python analysis/analyze_active_dataset.py
"""
import os, sys, json
sys.stdout.reconfigure(encoding='utf-8')
from collections import Counter, defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..'))
BASE = os.path.join(REPO, 'data', 'full_pool')
PROG = os.path.join(REPO, 'data', 'repro_progress.json')
RAW = os.path.join(REPO, 'data', 'real_raw')
FIG = os.path.join(REPO, 'figs'); os.makedirs(FIG, exist_ok=True)
plt.rcParams.update({'font.size': 9, 'axes.grid': True, 'grid.alpha': 0.3, 'figure.dpi': 200})

# ---------------------------------------------------------------------------
# Screening funnel (fixed, from the completed screening pipeline)
# ---------------------------------------------------------------------------
FUNNEL = [
    ('Official pure issues', 1343),
    ('Keyword-classified BUG', 439),
    ('Confirmed real bugs', 398),
    ('Fixed-in-current (removed)', 56),
    ('ACTIVE dataset', 342),
]

# ---------------------------------------------------------------------------
# TIER B: evidence-based exposure-channel classification for the 49 reproduced bugs.
# Each entry is (issue, origin, channel, note). channel is one of:
#   'pushed-server' | 'silent' | 'caller-exception' |
#   'single-layer-correct' | 'single-layer-masked' | 'registration-error'
# The note cites the raw evidence file / runtime message for traceability.
# ---------------------------------------------------------------------------
CHANNEL_CLASS = {
    # --- pushed to Server (origin != Server, reported at Server layer) ---
    110: ('Client', 'pushed-server', 'Error executing tool bad, is_error=True; real cause = non-UTF-8 bytes decode'),
    1361: ('Client', 'pushed-server', 'Error executing tool boom, is_error=True'),
    2114: ('Client', 'pushed-server', 'Error executing tool boom, is_error=True'),
    3637: ('Host', 'pushed-server', 'real_r_flat_argument.txt: Error executing tool summarize, is_error=True'),
    3572: ('Host', 'pushed-server', 'real_r_validation_echo_input.txt: Error executing tool lookup, is_error=True'),
    3579: ('Host', 'pushed-server', 'real_r_empty_server_components.txt: Unknown tool, is_error=True'),
    2741: ('Transport', 'pushed-server', 'Error executing tool boom, is_error=True; real cause only in "Session crashed" log'),
    # --- silent (is_error=False, logical error hidden) ---
    2057: ('Client', 'silent', 'HTTP 202; null-id accepted as notification, never rejected'),
    3067: ('Server', 'silent', 'call_tool(add,{typo:9}) -> 3, is_error=False; extra param silently dropped'),
    2539: ('Server', 'silent', '{"text": null}, is_error=False; wrong result shape returned'),
    2618: ('Transport', 'silent', 'HTTP 200; MCP-Protocol-Version header vs body mismatch not validated'),
    3549: ('Server', 'silent', 'real_r_race_lost_update.txt: 20 concurrent calls -> result 1, is_error=False (lost update)'),
    3578: ('Server', 'silent', 'real_r_duplicate_tool_shadow.txt: dup tool shadow -> 2, is_error=False'),
    3585: ('Server', 'silent', 'real_r_media_unregistered_mime.txt: image/jpg, is_error=False (unregistered mime accepted)'),
    3592: ('Server', 'silent', 'real_r_fallback_success_flag.txt: stale-cache-fallback, is_error=False'),
    3640: ('Server', 'silent', 'real_r_capabilities_drop.txt: is_error=False; advertised capabilities dropped'),
    3643: ('Server', 'silent', 'real_r_userlist_prompt.txt: is_error=False; PromptMessage stringified'),
    3646: ('Host', 'silent', 'real_r_extra_arg_silent.txt: extra arg -> 1, is_error=False'),
    # --- caller-exception (raw Python / HTTP exception in calling code) ---
    3556: ('Transport', 'caller-exception', 'real_r_session_reinit_404.txt: RAISED ExceptionGroup'),
    3557: ('Transport', 'caller-exception', 'real_r_jsonrpc_error_code.txt: HTTP 400, JSON-RPC -32602'),
    3560: ('Transport', 'caller-exception', 'real_r_tool_timeout.txt: RAISED ExceptionGroup (timeout)'),
    # --- single-layer-correct (Server-origin, correctly reported at Server) ---
    234: ('Server', 'single-layer-correct', 'Unknown tool: no_such_tool, is_error=True'),
    2422: ('Server', 'single-layer-correct', 'Unknown tool: no_such_tool, is_error=True'),
    1579: ('Server', 'single-layer-correct', 'RAISED MCPError: Unknown resource'),
    3342: ('Server', 'single-layer-correct', 'RAISED MCPError: Internal server error'),
    3351: ('Server', 'single-layer-correct', 'Error executing tool f: 1 validation error (detail retained)'),
    # --- single-layer-masked (Server-origin, at Server but real cause genericised) ---
    348: ('Server', 'single-layer-masked', 'Error executing tool img (real PydanticSchemaGenerationError hidden)'),
    417: ('Server', 'single-layer-masked', 'Error executing tool boom'),
    698: ('Server', 'single-layer-masked', 'Error executing tool boom'),
    743: ('Server', 'single-layer-masked', 'Error executing tool boom'),
    891: ('Server', 'single-layer-masked', 'Error executing tool f (real TypeError hidden)'),
    1060: ('Server', 'single-layer-masked', 'Error executing tool img'),
    1702: ('Server', 'single-layer-masked', 'Error executing tool get_name'),
    2153: ('Server', 'single-layer-masked', 'Error executing tool boom'),
    2386: ('Server', 'single-layer-masked', 'Error executing tool boom (CWE-209 sensitive value hidden)'),
    2431: ('Server', 'single-layer-masked', 'Error executing tool boom (McpError not pickle-safe)'),
    2770: ('Server', 'single-layer-masked', 'Error executing tool boom'),
    3099: ('Server', 'single-layer-masked', 'Error executing tool ext'),
    3266: ('Server', 'single-layer-masked', 'Error executing tool boom'),
    3656: ('Server', 'single-layer-masked', 'Error executing tool a'),
    3554: ('Server', 'single-layer-masked', 'real_r_bytes_output_crash.txt: Error executing tool get_bytes'),
    3569: ('Server', 'single-layer-masked', 'real_r_permission_swallow.txt: Error executing tool fragile2'),
    3586: ('Server', 'single-layer-masked', 'real_r_non_tool_error_silent.txt: Error executing tool fragile'),
    # --- registration-error (server cannot build / register) ---
    244: ('Server', 'registration-error', 'RAISED-AT-REG ValueError: URI template variables missing'),
    1974: ('Server', 'registration-error', 'RAISED-AT-REG AttributeError: Handler has no __name__'),
    3573: ('Server', 'registration-error', 'real_r_iterator_meta_fail.txt: RAISED-AT-REG PydanticSchemaGenerationError'),
    3341: ('Server', 'single-layer-correct', 'RAISED RuntimeError: Invalid structured content (nan)'),
    3385: ('Server', 'single-layer-correct', 'RAISED RuntimeError: Invalid structured content (inf)'),
    3644: ('Server', 'single-layer-correct', 'real_r_outputschema_mode.txt: RAISED RuntimeError invalid structured content'),
}


def channel_counts(repro):
    c = Counter(r['channel'] for r in repro)
    return c


def tier_a():
    """Descriptive statistics over the ACTIVE (342) dataset."""
    orig = json.load(open(os.path.join(BASE, 'origin_labels.json'), encoding='utf-8'))
    fixed = set(json.load(open(os.path.join(BASE, 'fixed_removed.json'), encoding='utf-8'))['removed_issues'])
    conf = {x['number']: x for x in json.load(open(os.path.join(BASE, 'confirmed_bugs.json'), encoding='utf-8'))}
    prog = json.load(open(PROG, encoding='utf-8'))

    active = [r for r in orig if r['number'] not in fixed]
    total = len(active)
    layer = Counter(r['origin'] for r in active)
    states = Counter(conf.get(r['number'], {}).get('state') for r in active)

    # reproduction status split over active
    rep_status = Counter()
    reason_cat = Counter()
    auth_skip = 0
    for r in active:
        n = r['number']
        p = prog.get(str(n), {})
        if p.get('status') == 'done':
            rep_status['reproduced'] += 1
        elif p.get('status') == 'limited':
            rep_status['limited'] += 1
            reason_cat[p.get('reason', '?').split(':')[0].strip()] += 1
        else:
            rep_status['auth-skipped'] += 1
            auth_skip += 1
            reason_cat['auth/credentials-required'] += 1

    out = {
        'funnel': dict(FUNNEL),
        'active_total': total,
        'removed_fixed': len(fixed),
        'confirmed_total': len(orig),
        'layer': dict(layer),
        'open': states.get('open', 0),
        'closed': states.get('closed', 0),
        'repro_status': dict(rep_status),
        'repro_reasons': dict(reason_cat.most_common()),
        'auth_skipped': auth_skip,
    }
    with open(os.path.join(BASE, 'active_dataset_analysis.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    return out


def tier_b():
    """Three-channel exposure model over the 49 REPRODUCED bugs (evidence-based)."""
    prog = json.load(open(PROG, encoding='utf-8'))
    active = [r for r in json.load(open(os.path.join(BASE, 'origin_labels.json'), encoding='utf-8'))
              if r['number'] not in set(json.load(open(os.path.join(BASE, 'fixed_removed.json'), encoding='utf-8'))['removed_issues'])]
    repro = []
    for r in active:
        n = r['number']
        if prog.get(str(n), {}).get('status') != 'done':
            continue
        if n not in CHANNEL_CLASS:
            continue
        origin, channel, note = CHANNEL_CLASS[n]
        repro.append({'issue': n, 'origin': origin, 'channel': channel, 'note': note})

    cc = channel_counts(repro)
    n = len(repro)

    # Mismatch = non-Server-origin exposed at a layer != origin.
    non_server = [r for r in repro if r['origin'] != 'Server']
    mismatch = [r for r in non_server if r['channel'] in ('pushed-server', 'caller-exception')]
    silent = [r for r in repro if r['channel'] == 'silent']
    # Message-masking = single-layer but real cause genericised away.
    masked = [r for r in repro if r['channel'] == 'single-layer-masked']

    # per-origin x channel for the figure
    by_origin = {}
    for o in ['Host', 'Client', 'Transport']:
        sub = [r for r in non_server if r['origin'] == o]
        by_origin[o] = {
            'pushed': sum(1 for r in sub if r['channel'] == 'pushed-server'),
            'silent': sum(1 for r in sub if r['channel'] == 'silent'),
            'caller': sum(1 for r in sub if r['channel'] == 'caller-exception'),
            'total': len(sub),
        }
    server = [r for r in repro if r['origin'] == 'Server']
    by_origin['Server'] = {
        'pushed': 0,
        'silent': sum(1 for r in server if r['channel'] == 'silent'),
        'caller': sum(1 for r in server if r['channel'] == 'caller-exception'),
        'correct': sum(1 for r in server if r['channel'] in ('single-layer-correct', 'single-layer-masked')),
        'registration': sum(1 for r in server if r['channel'] == 'registration-error'),
        'masked': sum(1 for r in server if r['channel'] == 'single-layer-masked'),
        'total': len(server),
    }

    out = {
        'reproduced_total': n,
        'channels': dict(cc),
        'non_server_total': len(non_server),
        'mismatch_count': len(mismatch),
        'mismatch_rate': round(len(mismatch) / len(non_server), 4) if non_server else 0,
        'mismatch_pushed_server': sum(1 for r in mismatch if r['channel'] == 'pushed-server'),
        'mismatch_caller_exception': sum(1 for r in mismatch if r['channel'] == 'caller-exception'),
        'silent_count': len(silent),
        'silent_rate': round(len(silent) / n, 4) if n else 0,
        'masked_count': len(masked),
        'masked_rate': round(len(masked) / n, 4) if n else 0,
        'by_origin': by_origin,
        'per_bug': repro,
    }
    with open(os.path.join(BASE, 'active_dataset_analysis.json'), 'w', encoding='utf-8') as fh:
        pass
    return out, repro


def fig_funnel():
    stages = [s for s, _ in FUNNEL]
    vals = [v for _, v in FUNNEL]
    fig, ax = plt.subplots(figsize=(7.0, 3.8))
    y = np.arange(len(stages))
    ax.barh(y, vals, color=['#4daf4a', '#ff7f00', '#e41a1c', '#999999', '#377eb8'], edgecolor='black', linewidth=0.5)
    for i, v in enumerate(vals):
        ax.text(v + 20, i, f'{v:,}', va='center', fontsize=9, weight='bold')
    ax.set_yticks(y); ax.set_yticklabels(stages, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel('Bugs'); ax.set_xlim(0, max(vals) * 1.18)
    ax.set_title('MCP-Fault-Benchmark screening funnel (single library, python-sdk)', fontsize=10)
    plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig_funnel.png')); plt.close()


def fig_exposure(repro):
    CH = {'pushed-server': 'Pushed to Server (wrong layer)',
          'silent': 'Silent (hidden, no error flag)',
          'caller-exception': 'Caller exception (raw Python/HTTP)'}
    order = ['Host', 'Client', 'Transport']
    pushed = [sum(1 for r in repro if r['origin'] == o and r['channel'] == 'pushed-server') for o in order]
    silent = [sum(1 for r in repro if r['origin'] == o and r['channel'] == 'silent') for o in order]
    caller = [sum(1 for r in repro if r['origin'] == o and r['channel'] == 'caller-exception') for o in order]
    fig, ax = plt.subplots(figsize=(7.0, 4.2)); x = np.arange(len(order))
    ax.bar(x, pushed, label=CH['pushed-server'], color='#7570b3')
    ax.bar(x, silent, bottom=pushed, label=CH['silent'], color='#e41a1c')
    ax.bar(x, caller, bottom=np.array(pushed) + np.array(silent), label=CH['caller-exception'], color='#1b9e77')
    for i in range(len(order)):
        tot = pushed[i] + silent[i] + caller[i]
        if tot:
            ax.text(i, tot + 0.3, f'{tot}', ha='center', fontsize=9, weight='bold')
            if pushed[i]: ax.text(i, pushed[i] / 2, str(pushed[i]), ha='center', va='center', color='white', fontsize=9)
            if silent[i]: ax.text(i, pushed[i] + silent[i] / 2, str(silent[i]), ha='center', va='center', color='white', fontsize=9)
            if caller[i]: ax.text(i, pushed[i] + silent[i] + caller[i] / 2, str(caller[i]), ha='center', va='center', color='white', fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels([o + '-origin' for o in order], fontsize=9)
    ax.set_ylabel('Reproduced bugs'); ax.set_ylim(0, max(pushed) + max(silent) + max(caller) + 2)
    ax.set_title('How non-Server MCP bugs are actually exposed (n=49 reproduced)', fontsize=10)
    ax.legend(loc='upper right', fontsize=8)
    plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig_exposure_channels.png')); plt.close()


def fig_reasons(a):
    cats = a['repro_reasons']
    cats = dict(sorted(cats.items(), key=lambda kv: -kv[1]))
    labels = list(cats.keys()); vals = list(cats.values())
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    y = np.arange(len(labels))
    ax.barh(y, vals, color='#377eb8', edgecolor='black', linewidth=0.5)
    for i, v in enumerate(vals):
        ax.text(v + 2, i, str(v), va='center', fontsize=9, weight='bold')
    ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=8); ax.invert_yaxis()
    ax.set_xlabel('Bugs'); ax.set_xlim(0, max(vals) * 1.15)
    ax.set_title('Why the other bugs cannot be reproduced / are hard to localise (n=342)', fontsize=10)
    plt.tight_layout(); plt.savefig(os.path.join(FIG, 'fig_repro_reasons.png')); plt.close()


def main():
    a = tier_a()
    b, repro = tier_b()
    print('=' * 72)
    print('TIER A  - ACTIVE dataset (342) descriptive statistics')
    print('=' * 72)
    print(f"  funnel : " + ' -> '.join(f'{v:,}' for _, v in FUNNEL))
    print(f"  layer  : " + ', '.join(f'{k} {v}' for k, v in a['layer'].items()))
    print(f"  state  : open {a['open']} / closed {a['closed']}")
    print(f"  repro  : " + ', '.join(f'{k} {v}' for k, v in a['repro_status'].items()))
    print(f"\n  why-limited reasons:")
    for k, v in a['repro_reasons'].items():
        print(f"    {v:4d}  {k}")
    print()
    print('=' * 72)
    print('TIER B  - three-channel exposure model (49 reproduced bugs, evidence-based)')
    print('=' * 72)
    print('  channel counts      : ' + ', '.join(f'{k} {v}' for k, v in b['channels'].items()))
    print(f"  non-Server-origin   : {b['non_server_total']}")
    print(f"  MISMATCH            : {b['mismatch_count']}/{b['non_server_total']} = {b['mismatch_rate']*100:.1f}%")
    print(f"    pushed-to-Server  : {b['mismatch_pushed_server']}")
    print(f"    caller-exception  : {b['mismatch_caller_exception']}")
    print(f"  SILENT              : {b['silent_count']}/{b['reproduced_total']} = {b['silent_rate']*100:.1f}%")
    print(f"  generic-masked      : {b['masked_count']}/{b['reproduced_total']} = {b['masked_rate']*100:.1f}%")
    print(f"\n  per-origin breakdown:")
    for o, d in b['by_origin'].items():
        print(f"    {o:<10s} {d}")
    # merge both into one json
    a.update({'tier_b': b})
    with open(os.path.join(BASE, 'active_dataset_analysis.json'), 'w', encoding='utf-8') as fh:
        json.dump(a, fh, ensure_ascii=False, indent=2)
    fig_funnel(); fig_exposure(repro); fig_reasons(a)
    print('\n-> data/full_pool/active_dataset_analysis.json')
    print('-> figs/fig_funnel.png, figs/fig_exposure_channels.png, figs/fig_repro_reasons.png')


if __name__ == '__main__':
    main()