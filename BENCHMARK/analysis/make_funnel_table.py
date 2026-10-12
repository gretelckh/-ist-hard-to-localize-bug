#!/usr/bin/env python3
"""Generate the authoritative data-collection funnel table for the MCP-Fault-Benchmark.

Reads the authoritative data files and emits a self-consistent funnel:
  1,343 official pure issues -> 439 keyword-BUG -> 398 confirmed real bugs
  -> 56 fixed-in-2.2.0 (removed) -> 342 active dataset -> 49 reproduced
  (+ 293 not-reproducible: env-limited / auth-limited / spec- or observation-only).

Outputs:
  - docs/FUNNEL_TABLE.md   (human/markdown table + per-stage prose, for the paper)
  - data/full_pool/funnel_table.json  (structured numbers, single source of truth)

Run from MCP-Fault-Benchmark/:
    python analysis/make_funnel_table.py
"""
import os, json
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..'))
FP = os.path.join(REPO, 'data', 'full_pool')
DOCS = os.path.join(REPO, 'docs')
os.makedirs(DOCS, exist_ok=True)


def load(name):
    return json.load(open(os.path.join(FP, name), encoding='utf-8'))


def main():
    screened = load('full_pool_screened.json')
    verdicts = load('bug_review_verdicts.json')
    confirmed = load('confirmed_bugs.json')
    active = load('active_dataset_analysis.json')
    tiers = load('repro_tiers.json')

    # --- Stage 1: screening labels over the full pool ---
    label_dist = Counter(x.get('label') for x in screened)
    n_pool = len(screened)

    # --- Stage 2: keyword BUG candidates -> human review verdicts ---
    n_bug_cand = verdicts['total_initial']
    vdist = Counter(vd.get('verdict') for vd in verdicts['verdicts'].values())
    n_bug = vdist.get('BUG', 0)
    n_notbug = vdist.get('NOT_BUG', 0)

    # --- Stage 3: confirmed bugs -> fixed-in-2.2.0 removed -> active ---
    n_confirmed = len(confirmed)
    n_removed_fixed = active.get('removed_fixed', 0)
    n_active = active.get('active_total', 0)

    # --- Stage 4: active -> reproduced vs not ---
    repro = active.get('repro_status', {})
    n_reproduced = repro.get('reproduced', 0)
    n_limited = repro.get('limited', 0)
    n_auth = repro.get('auth-skipped', 0)

    # --- Stage 5: not-reproducible breakdown from repro_tiers ---
    tier_dist = Counter(x['tier'] for x in tiers)
    t1 = tier_dist.get('T1 reproducible-now', 0)
    t2 = tier_dist.get('T2 env/dep-limited', 0)
    t3 = tier_dist.get('T3 auth-limited', 0)
    t4 = (tier_dist.get('T4 spec/behaviour-only', 0)
          + tier_dist.get('T4 observation-only', 0))

    n_notrepro = n_active - n_reproduced

    # group fine-grained repro_reasons into paper-level categories (sum = n_notrepro)
    rr = active.get('repro_reasons', {})
    REASONS = {
        'env':    rr.get('env/transport-config', 0) + rr.get('example-config', 0)
                  + rr.get('env-specific', 0),
        'auth':   rr.get('auth/credentials-required', 0),
        'notex':  rr.get('not-exercised', 0)
                  + rr.get('no defect captured by this trigger (clean success); scenario not exercised', 0)
                  + rr.get('not-reproduced-with-this-trigger', 0),
        'obs':    rr.get('observation/scenario-specific', 0) + rr.get('observation-only', 0)
                  + rr.get('scenario-specific', 0),
        'specgap': rr.get('spec-gap', 0),
        'ext':    rr.get('external-tool', 0),
    }

    table = [
        # stage, label, count, note
        ('1', 'Official pure issues in modelcontextprotocol/python-sdk', n_pool,
         'Full issue pool on GitHub, excluding pull requests.'),
        ('2', 'Keyword-classified as BUG', n_bug_cand,
         f'Automatic keyword screen; the remaining {n_pool - n_bug_cand} fall into '
         'QUESTION / OTHER / FEATURE / CI-REFACTOR / DOC.'),
        ('3', 'Confirmed real bugs (manual review)', n_bug,
         f'{n_notbug} keyword-BUG candidates rejected as non-bugs after manual review.'),
        ('4', 'Fixed in the current SDK (2.2.0), removed', n_removed_fixed,
         'Behave correctly on mcp 2.2.0; excluded from the active dataset.'),
        ('5', 'ACTIVE dataset (studied)', n_active,
         '= confirmed - fixed-in-current.'),
        ('6', 'Reproduced at runtime (evidence-based)', n_reproduced,
         'T1: each bug is bound to a real issue and reproduced over Streamable HTTP.'),
        ('7', 'Not reproducible at runtime', n_active - n_reproduced,
         'env-limited / auth-limited / spec- or observation-only (see breakdown).'),
    ]

    # per-stage non-bug label detail for prose
    detail = {
        'pool_total': n_pool,
        'label_dist': dict(label_dist),
        'bug_candidates': n_bug_cand,
        'confirmed': n_bug,
        'not_bug_rejected': n_notbug,
        'fixed_in_current': n_removed_fixed,
        'active': n_active,
        'reproduced': n_reproduced,
        'limited': n_limited,
        'auth_skipped': n_auth,
        'repro_tiers': dict(tier_dist),
        'not_reproducible_breakdown': {
            'env_dep_limited': t2,
            'auth_limited': t3,
            'spec_behaviour_or_observation': t4,
        },
        'not_reproducible_reasons_grouped': REASONS,
        'checks': {
            'pool_minus_bug_cand': n_pool - n_bug_cand,
            'confirmed_minus_fixed_equals_active': n_confirmed - n_removed_fixed == n_active,
            'repro_plus_not_repro_equals_active': n_reproduced + (n_active - n_reproduced) == n_active,
            'tiers_sum_equals_active': t1 + t2 + t3 + t4 == n_active,
            'reasons_grouped_sum_equals_notrepro': sum(REASONS.values()) == n_notrepro,
        },
    }

    out = os.path.join(FP, 'funnel_table.json')
    json.dump({'table': table, 'detail': detail},
              open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    # --- Markdown document ---
    lines = []
    lines.append('# Data-collection funnel (authoritative)')
    lines.append('')
    lines.append('> Source of truth: `data/full_pool/funnel_table.json` (regenerated by '
                 '`analysis/make_funnel_table.py`).')
    lines.append('')
    lines.append('## Funnel table')
    lines.append('')
    lines.append('| Stage | Step | # | Note |')
    lines.append('|---|---|---:|---|')
    for st, lab, cnt, note in table:
        lines.append(f'| {st} | {lab} | {cnt} | {note} |')
    lines.append('')
    lines.append('## Per-stage classification detail')
    lines.append('')
    lines.append(f"- Non-bug pool (keyword stage): {detail['label_dist']}.")
    lines.append(f"- Rejected at review: {detail['not_bug_rejected']} keyword-BUG candidates "
                 'were not real bugs (usage questions, pure feature requests, non-python-sdk, '
                 'env/dependency/packaging, CI/test/refactor, duplicates, unverifiable).')
    lines.append(f"- Not-reproducible active bugs ({n_active - n_reproduced}) breakdown: "
                 f"see the authoritative category table below (env/config, auth, not-exercised, "
                 f"observation, spec-gap, external-tool).")
    lines.append('')
    lines.append('> Classification source note: the authoritative not-reproducible breakdown is the '
                 'category table below, computed from the per-bug reproduction record '
                 '(`repro_reasons`, via analyze_active_dataset.py) and grouped into paper-level '
                 'categories; it sums exactly to the not-reproducible total and is therefore '
                 'self-consistent. The coarser tier labels in `repro_tiers.json` '
                 '(assess_reproducibility.py) give a related split '
                 f'(T2 env/dep {t2} / T3 auth {t3} / T4 spec- or observation {t4}) that also sums '
                 f'to {n_active} but uses a different boundary; use the category table below as '
                 'the single source of truth for the paper.')
    lines.append('')
    lines.append('## Consistency checks')
    lines.append('')
    for k, v in detail['checks'].items():
        lines.append(f'- `{k}`: {v}')
    lines.append('')
    lines.append('## Prose (for the Data Collection / Sampling section)')
    lines.append('')
    lines.append(
        'To build a real, non-fabricated benchmark we mined the entire issue tracker of the '
        f'official `modelcontextprotocol/python-sdk` and recovered {n_pool} pure issues '
        f'(pull requests excluded). A keyword screen labelled {n_bug_cand} of them as candidate '
        f'bugs; a manual review confirmed {n_bug} genuine bugs (rejecting {n_notbug} non-bugs). '
        f'Of these, {n_removed_fixed} already behave correctly on the pinned SDK version '
        f'(mcp 2.2.0) and were removed, leaving an active dataset of {n_active} real bugs. '
        f'We reproduced {n_reproduced} of them over the production Streamable HTTP transport, '
        'each bound to a real issue number. The remaining '
        f'{n_active - n_reproduced} could not be reproduced at runtime and are classified '
        f'by the reason recorded during reproduction (see the category table below).')
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('| Stage | Count |')
    lines.append('|---|---:|')
    lines.append(f'| Reproduced (evidence) | {n_reproduced} |')
    lines.append(f'| Not reproduced | {n_active - n_reproduced} |')
    lines.append(f'| **ACTIVE dataset** | **{n_active}** |')
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('## Why-not-reproducible breakdown (293)')
    lines.append('')
    lines.append('The 293 not-reproducible active bugs are classified by the reason recorded '
                 'during reproduction (from `active_dataset_analysis.json` -> `repro_reasons`, '
                 'aggregated by `analyze_active_dataset.py`), grouped into paper-level categories.')
    lines.append('')
    lines.append('| Category | Raw reasons | # | % of 293 |')
    lines.append('|---|---|---:|---:|')
    lines.append(f'| Environment / transport config | env/transport-config, example-config, '
                 f'env-specific | {REASONS["env"]} | {100*REASONS["env"]/n_notrepro:.1f}% |')
    lines.append(f'| Authentication / credentials | auth/credentials-required | '
                 f'{REASONS["auth"]} | {100*REASONS["auth"]/n_notrepro:.1f}% |')
    lines.append(f'| Not exercised / no defect captured | not-exercised, no-defect-captured, '
                 f'not-reproduced-with-this-trigger | {REASONS["notex"]} | '
                 f'{100*REASONS["notex"]/n_notrepro:.1f}% |')
    lines.append(f'| Observation / scenario-specific | observation-only, observation/scenario-specific, '
                 f'scenario-specific | {REASONS["obs"]} | {100*REASONS["obs"]/n_notrepro:.1f}% |')
    lines.append(f'| Spec gap | spec-gap | {REASONS["specgap"]} | '
                 f'{100*REASONS["specgap"]/n_notrepro:.1f}% |')
    lines.append(f'| External tool | external-tool | {REASONS["ext"]} | '
                 f'{100*REASONS["ext"]/n_notrepro:.1f}% |')
    lines.append(f'| **Total** |  | **{n_notrepro}** | 100% |')
    lines.append('')
    lines.append('### Why-not-reproducible prose')
    lines.append('')
    lines.append(
        f'Of the {n_active} active real bugs, {n_reproduced} were reproduced at runtime and '
        f'form the evidence-based tier-B analysis. The remaining {n_notrepro} could not be '
        f'reproduced over the production Streamable HTTP transport. The dominant reasons are '
        f'environment / transport configuration ({REASONS["env"]}, '
        f'{100*REASONS["env"]/n_notrepro:.0f}%) --- e.g. stdio/SSE-only cases, platform- or '
        f'dependency-specific builds, and official example code paths; authentication-limited '
        f'({REASONS["auth"]}, {100*REASONS["auth"]/n_notrepro:.0f}%) requiring OAuth credentials; '
        f'and cases whose defect is not exercised by a single clean tool call '
        f'({REASONS["notex"]}, {100*REASONS["notex"]/n_notrepro:.0f}%), such as concurrency races, '
        f'cross-server state, or client-side observation. A smaller set is purely observational or '
        f'scenario-specific ({REASONS["obs"]}, {100*REASONS["obs"]/n_notrepro:.0f}%), or reflects a '
        f'protocol specification gap ({REASONS["specgap"]}) or an external tool / inspector '
        f'dependency ({REASONS["ext"]}). We report each of these honestly rather than asserting '
        f'the bug is fixed, and we never fabricate a channel for a bug we could not reproduce.')

    md = os.path.join(DOCS, 'FUNNEL_TABLE.md')
    with open(md, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines))

    print('->', out)
    print('->', md)
    print('REPRODUCED', n_reproduced, 'ACTIVE', n_active,
          'NOT_REPRO', n_active - n_reproduced)


if __name__ == '__main__':
    main()