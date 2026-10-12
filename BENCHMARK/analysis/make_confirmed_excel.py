"""Generate confirmed_bugs.xlsx (398 real bugs) + enrich confirmed_bugs.json.

Enriches the 398 confirmed bugs with available fields (state, created_at, body_head,
issue URL) and writes a clean Excel for review/reporting.

Run from MCP-Fault-Benchmark/:
    python analysis/make_confirmed_excel.py
"""
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
import openpyxl
from openpyxl.styles import Font

HERE = os.path.dirname(os.path.abspath(__file__))
POOL = os.path.normpath(os.path.join(HERE, '..', 'data', 'full_pool', 'full_pool_screened.json'))
CONF = os.path.normpath(os.path.join(HERE, '..', 'data', 'full_pool', 'confirmed_bugs.json'))
OUT = os.path.normpath(os.path.join(HERE, '..', 'data', 'full_pool', 'confirmed_bugs.xlsx'))

HEADER = ['序号', 'Issue', '标题', '状态', '创建时间', 'GitHub链接', 'body前300字']


def main():
    pool = json.load(open(POOL, encoding='utf-8'))
    by = {x['number']: x for x in pool}
    conf = json.load(open(CONF, encoding='utf-8'))
    conf.sort(key=lambda x: x['number'])

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'confirmed_bugs'
    ws.append(HEADER)
    for i, c in enumerate(conf, 1):
        n = c['number']
        p = by.get(n, {})
        ws.append([
            i,
            n,
            c['title'],
            p.get('state', ''),
            (p.get('created_at') or '')[:10],
            c.get('url', ''),
            (p.get('body_head') or '')[:300],
        ])
    for cell in ws[1]:
        cell.font = Font(bold=True)
    ws.freeze_panes = 'A2'
    wb.save(OUT)

    # enrich confirmed_bugs.json with available fields
    enriched = []
    for c in conf:
        n = c['number']
        p = by.get(n, {})
        enriched.append({
            'number': n,
            'title': c['title'],
            'state': p.get('state', ''),
            'created_at': p.get('created_at', ''),
            'url': c.get('url', ''),
            'body_head': (p.get('body_head') or '')[:300],
        })
    json.dump(enriched, open(CONF, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('confirmed_bugs.xlsx ->', OUT, '(', len(conf), 'rows )')
    print('confirmed_bugs.json enriched ->', len(enriched), 'records')


if __name__ == '__main__':
    main()