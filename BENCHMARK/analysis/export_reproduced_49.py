#!/usr/bin/env python3
"""Export the 49 reproduced bugs (three-channel classification) to a CSV for
the paper table, plus print the classification for drafting."""
import json, os, csv, sys
sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, '..', 'data', 'full_pool'))
AN = os.path.join(BASE, 'active_dataset_analysis.json')
CONF = os.path.join(BASE, 'confirmed_bugs.json')

an = json.load(open(AN, encoding='utf-8'))
conf = {x['number']: x for x in json.load(open(CONF, encoding='utf-8'))}
per = {b['issue']: b for b in an['tier_b']['per_bug']}

CH = {
    'pushed-server': 'pushed-to-Server',
    'silent': 'silent',
    'caller-exception': 'caller-exception',
    'single-layer-correct': 'single-layer (correct)',
    'single-layer-masked': 'single-layer (genericised)',
    'registration-error': 'registration',
}

rows = []
for i in sorted(per):
    b = per[i]
    c = conf.get(i, {})
    rows.append({
        'issue': '#' + str(i),
        'origin': b['origin'],
        'channel': CH.get(b['channel'], b['channel']),
        'title': c.get('title', ''),
        'note': b['note'],
    })

# print concise classification
print('=== 49 reproduced bugs: issue | origin | channel ===')
for r in rows:
    print(f"{r['issue']:>6}  {r['origin']:9s}  {r['channel']:26s}  {r['title'][:52]}")

# write CSV
out_csv = os.path.join(BASE, 'reproduced_49_channels.csv')
with open(out_csv, 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['GitHub Issue', 'Origin Layer', 'Exposure Channel', 'Bug Title', 'Root-cause note'])
    for r in rows:
        w.writerow([r['issue'], r['origin'], r['channel'], r['title'], r['note']])
print('\n->', out_csv)

# per-origin x channel cross-tab (for the figure/table)
print('\n=== per-origin x channel (13 non-Server + 36 Server) ===')
print(json.dumps(an['tier_b']['by_origin'], ensure_ascii=False, indent=2))