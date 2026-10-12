import json, sys, glob, os, re
sys.stdout.reconfigure(encoding='utf-8')
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(REPO, 'data', 'raw')

ORIGIN = {
    'h1_tool_not_exist':'Host','h2_missing_param':'Host','h3_wrong_param_name':'Host','h4_wrong_param_type':'Host',
    'c1_extra_param':'Client','c2_wrong_nesting':'Client','c3_invalid_enum':'Client','c4_wrong_method':'Client',
    's1_divide_by_zero':'Server','s2_index_out_of_range':'Server','s3_assertion_error':'Server','s4_custom_exception':'Server',
    's5_oversized_response':'Server','s6_pydantic_serialize_error':'Server','s7_duplicate_tool_registration':'Server','s8_auth_error':'Server',
    't1_session_closed':'Transport','t2_request_cancelled':'Transport','t3_invalid_message':'Transport','t4_timing_error':'Transport',
}

def reported_layer(txt):
    """From the RAW captured text, infer the layer at which the fault is EXPOSED.
    Evidence-based, no hardcoded scope. Returns one of Server/Client/Silent/Unknown/Host."""
    if 'is_error=False' in txt:
        return 'Silent'          # SDK returned success (silent, or a legit success)
    if 'Error executing tool' in txt:
        return 'Server'          # MCP tool-dispatch surfaced at Server tool pipeline
    if 'is_error=True' in txt:
        return 'Server'
    # Python exceptions surfaced in the Client/caller code (transport timing / cancellation)
    if ('CancelledError' in txt or
            'Client must be used within an async context manager' in txt or
            'TimeoutError' in txt or 'ExceptionGroup' in txt):
        return 'Client'
    if 'Unknown tool' in txt:
        return 'Server'          # dispatched/validated on the server side
    return 'Unknown'

rows = []
for raw in sorted(glob.glob(os.path.join(RAW, '*.txt'))):
    b = os.path.basename(raw)
    if b.startswith('_index'):
        continue
    parts = b.replace('.txt', '').split('_')
    variant = parts[0]
    case = '_'.join(parts[1:])
    for lk in ('host','client','server','transport'):
        if case.endswith('_' + lk):
            case = case[:-(len(lk)+1)]
            break
    txt = open(raw, encoding='utf-8', errors='replace').read()
    orig = ORIGIN.get(case, '?')
    rep = reported_layer(txt)
    rows.append({'case':case,'variant':variant,'origin':orig,'reported':rep})

print('='*70)
print('OBSERVATION-DRIVEN reported-layer vs origin (all 80 runs, read from raw files)')
print('='*70)
ct = Counter((x['origin'], x['reported']) for x in rows)
print(f"{'origin':<10}{'reported':<10}count")
for k,v in sorted(ct.items()):
    print(f"{k[0]:<10}{k[1]:<10}{v}")
print()
print('=== Mismatch: non-Server origin, reported at a DIFFERENT layer (evidence-based) ===')
non_server = [x for x in rows if x['origin'] != 'Server']
mism = [x for x in non_server if x['reported'] != x['origin'] and x['reported'] != 'Unknown']
print(f'non-Server runs   : {len(non_server)}')
print(f'  reported=orig   : {sum(1 for x in non_server if x["reported"]==x["origin"])}')
print(f'  mismatch        : {len(mism)}')
print(f'  unknown evidence: {sum(1 for x in non_server if x["reported"]=="Unknown")}')
print()
print('--- where non-Server faults are actually reported ---')
for k,v in Counter(x['reported'] for x in non_server).most_common():
    print(f'  {k:<10}{v}')

# Save observation-driven dataset
out = os.path.join(REPO, 'data', 'obs_reported_layer.json')
json.dump(rows, open(out,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'\nsaved -> data/obs_reported_layer.json')