#!/usr/bin/env python3
"""Re-classify the 49 reproduced bugs by ROOT-CAUSE category (not exposure channel).

The three-channel model describes HOW the SDK *exposes* a fault. That is NOT the same as
WHY the bug exists. This script assigns each of the 49 bugs a root-cause category, so an
alluvial / sankey figure can flow origin-layer -> root-cause, and the paper can clearly
state that the layer is a *classification dimension*, not the root cause.

Categories (root cause):
  - err-masked      : the SDK strips the real exception value / root cause (genericised)
  - err-type-code   : wrong error type / error code / is_error semantics
  - silent-arg      : input / argument silently ignored or coerced (extra=ignore, type coercion)
  - serialization   : schema / serialization / validation failure (pydantic, non-finite, None)
  - concurrency     : concurrency / lifecycle / timeout race (lost update, dup reg, session)
  - protocol-spec   : protocol / specification violation (header mismatch, id:null, 405)
  - discovery       : unknown tool / unknown resource (discovery / routing)
  - registration    : server cannot build / register a tool at startup

Output: data/full_pool/rootcause_49.json  (issue -> origin, exposure channel, root-cause cat)
"""
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, '..', 'data', 'full_pool'))
AN = os.path.join(BASE, 'active_dataset_analysis.json')
OUT = os.path.join(BASE, 'rootcause_49.json')

# issue -> root-cause category
ROOT = {
    # ---- err-masked: real exception value / root cause stripped ----
    348: 'err-masked', 417: 'err-masked', 698: 'err-masked', 743: 'err-masked',
    891: 'err-masked', 1060: 'err-masked', 1702: 'err-masked', 2153: 'err-masked',
    2386: 'err-masked', 2431: 'err-masked', 2770: 'err-masked', 3099: 'err-masked',
    3266: 'err-masked', 3554: 'err-masked', 3569: 'err-masked', 3586: 'err-masked',
    3656: 'err-masked',
    # ---- err-type-code: wrong error type / code / is_error semantics ----
    234: 'err-type-code', 2422: 'err-type-code', 1579: 'err-type-code', 3342: 'err-type-code',
    3351: 'err-type-code', 3557: 'err-type-code',
    # ---- silent-arg: input / arg silently ignored or coerced ----
    3067: 'silent-arg', 3646: 'silent-arg',
    # ---- serialization: schema / serialization / validation failure ----
    2539: 'serialization', 3341: 'serialization', 3385: 'serialization', 3644: 'serialization',
    # ---- concurrency: concurrency / lifecycle / timeout race ----
    3549: 'concurrency', 3578: 'concurrency', 3556: 'concurrency', 3560: 'concurrency',
    # ---- protocol-spec: protocol / specification violation ----
    2618: 'protocol-spec', 3592: 'protocol-spec', 3640: 'protocol-spec', 3643: 'protocol-spec',
    2057: 'protocol-spec',
    # ---- discovery: unknown tool / resource ----
    3579: 'discovery',
    # ---- registration: server cannot build / register ----
    244: 'registration', 1974: 'registration', 3573: 'registration',
    # ---- pushed-server group: root causes ----
    110: 'err-masked', 1361: 'err-masked', 2114: 'err-masked', 2741: 'err-masked',
    3572: 'serialization', 3637: 'serialization',
    # ---- remaining silent that are actually serialization / protocol ----
    3585: 'serialization',
}

CAT_LABEL = {
    'err-masked': 'Error value / root cause stripped',
    'err-type-code': 'Wrong error type / code / is_error',
    'silent-arg': 'Argument silently ignored / coerced',
    'serialization': 'Schema / serialization / validation failure',
    'concurrency': 'Concurrency / lifecycle / timeout race',
    'protocol-spec': 'Protocol / spec violation',
    'discovery': 'Unknown tool / resource (discovery)',
    'registration': 'Server cannot build / register',
}
CAT_COLOR = {
    'err-masked': '#e6a817', 'err-type-code': '#7570b3', 'silent-arg': '#e41a1c',
    'serialization': '#4daf4a', 'concurrency': '#1b9e77', 'protocol-spec': '#f781bf',
    'discovery': '#377eb8', 'registration': '#999999',
}


def main():
    an = json.load(open(AN, encoding='utf-8'))
    per = {b['issue']: b for b in an['tier_b']['per_bug']}
    rows = []
    for i in sorted(per):
        b = per[i]
        cat = ROOT.get(i)
        if cat is None:
            raise SystemExit(f'UNCLASSIFIED issue {i}')
        rows.append({
            'issue': i, 'origin': b['origin'], 'exposure_channel': b['channel'],
            'root_cause': cat, 'root_cause_label': CAT_LABEL[cat],
            'note': b['note'],
        })
    json.dump({'items': rows, 'categories': CAT_LABEL, 'colors': CAT_COLOR},
              open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    from collections import Counter
    c = Counter((r['origin'], r['root_cause']) for r in rows)
    print('=== origin -> root-cause (49) ===')
    for (o, rc), n in sorted(c.items()):
        print(f'  {o:9s} -> {CAT_LABEL[rc]:42s} : {n}')
    print()
    print('=== root-cause total ===')
    for rc, n in Counter(r['root_cause'] for r in rows).most_common():
        print(f'  {n:3d}  {CAT_LABEL[rc]}')
    print('\n->', OUT)


if __name__ == '__main__':
    main()