#!/usr/bin/env python3
"""Build the unified 'all bug analysis table' (all_bugs_analysis.xlsx).

Merges the two header groups the author provided (deduped) into ONE comprehensive table
listing all 398 confirmed bugs. Columns that are already known are filled now; columns
that need the reproduction / exposure experiment are left blank and filled later
(Step 4: reported layer / exposure channel / scope).

Header (merged, deduped):
  序号 | Case ID | GitHub Issue | 链接 | 标题 | 状态 | 创建时间
  | 原始层(origin) | 标签来源 | 待复核
  | 故障分层 | 脚本文件名 | 故障描述 | 触发代码片段 | 异常类型 | 完整报错文本 | 故障范围标记

Filled now (from existing data):
  - 序号/Case ID/GitHub Issue/链接/标题/状态/创建时间            from confirmed_bugs.json
  - 原始层/标签来源/待复核                                       from origin_labels.json
  - 故障分层 = 原始层 (origin)  for now
  - 故障描述/触发代码片段/异常类型/完整报错文本                   for the reproduced bugs only
  - 脚本文件名, 故障范围标记                                      left blank (per author)

Run from MCP-Fault-Benchmark/:
    python analysis/make_all_bugs_excel.py
"""
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
CONF = os.path.normpath(os.path.join(HERE, '..', 'data', 'full_pool', 'confirmed_bugs.json'))
ORIG = os.path.normpath(os.path.join(HERE, '..', 'data', 'full_pool', 'origin_labels.json'))
VERINFO = os.path.normpath(os.path.join(HERE, '..', 'data', 'full_pool', '_verified_repro_info.json'))
PROG = os.path.normpath(os.path.join(HERE, '..', 'data', 'repro_progress.json'))
OUT = os.path.normpath(os.path.join(HERE, '..', 'data', 'full_pool', 'all_bugs_analysis.xlsx'))
# Bugs already FIXED in mcp 2.2.0 (T1-fixed) are REMOVED from the active dataset (350).
# The raw 398 survey pool stays in confirmed_bugs.json; only this active-analysis table excludes
# them. See data/full_pool/fixed_removed.json.
FIXED_FILE = os.path.normpath(os.path.join(HERE, '..', 'data', 'full_pool', 'fixed_removed.json'))

# repro case trigger (method/target/args) for the new batch-1 bugs, keyed by issue
NEW_TRIGGER = {
    234: ('call_tool', 'no_such_tool', '{}'),
    348: ('call_tool', 'img', '{}'),
    2114: ('call_tool', 'boom', '{}'),
    2422: ('call_tool', 'no_such_tool', '{}'),
    3266: ('call_tool', 'boom', "{'x': 1}"),
    1702: ('call_tool', 'get_name', '{}'),
    3342: ('get_prompt', 'p', '{}'),
}
NEW_DESC = {
    234: 'unknown tool returns is_error=False',
    348: 'no way to set isError=True for arbitrary tool result',
    2114: 'ExceptionGroup wrapping obscures real errors',
    2422: 'ToolNotFoundError vs ToolError for easier handling',
    3266: 'log exceptions raised in tool calls',
    1702: 'tool output fails outputSchema validation -> generic Error executing tool, hides schema detail',
    3342: 'prompt validation error -> generic MCPError: Internal server error, hides real validation error',
}


def main():
    conf = json.load(open(CONF, encoding='utf-8'))
    bynum = {x['number']: x for x in conf}
    orig = json.load(open(ORIG, encoding='utf-8'))
    ver = json.load(open(VERINFO, encoding='utf-8'))
    prog = json.load(open(PROG, encoding='utf-8'))

    # Remove bugs already FIXED in mcp 2.2.0 from the active dataset (user decision 2026-10-10).
    fixed_removed = set()
    if os.path.exists(FIXED_FILE):
        fixed_removed = set(json.load(open(FIXED_FILE, encoding='utf-8')).get('removed_issues', []))
    orig = [r for r in orig if r['number'] not in fixed_removed]
    conf = [x for x in conf if x['number'] not in fixed_removed]

    # reproducible code source (for traceability): issue -> (script, builder, trigger)
    sys.path.insert(0, os.path.normpath(os.path.join(HERE, '..', 'runner')))
    import repro_cases as rc
    code_src = {}
    for n, c in rc.CASES.items():
        builder = getattr(c.builder, '__name__', 'None') if c.builder else 'conn-refused'
        code_src[n] = (c.desc, f'repro_cases.py::{builder}', f'{c.method}({c.target}, {c.args})')

    headers = ['序号', 'Case ID', 'GitHub Issue', '链接', '标题', '状态', '创建时间',
               '原始层(origin)', '标签来源', '待复核',
               '故障分层', '复现状态', '是否能复现', '不能复现的原因', '脚本文件名',
               '故障描述', '触发代码片段', '异常类型', '完整报错文本', '故障范围标记']
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = 'all_bugs_analysis'
    ws.append(headers)
    for h in headers:
        c = ws[f'{chr(65+headers.index(h))}1']
        c.font = Font(bold=True, color='FFFFFF')
        c.fill = PatternFill('solid', fgColor='4472C4')
        c.alignment = Alignment(horizontal='center', vertical='center')
    green = PatternFill('solid', fgColor='C6EFCE')

    for i, r in enumerate(orig, start=2):
        n = r['number']
        rec = bynum.get(n, {})
        reproduced = (str(n) in ver) or (n in rc.CASES and prog.get(str(n), {}).get('status') == 'done'
                                    and prog.get(str(n), {}).get('defect_captured'))
        row = [i-1, 'BUG-%04d' % n, '#' + str(n), rec.get('url') or r.get('url') or '',
               rec.get('title') or r.get('title') or '', rec.get('state') or '',
               rec.get('created_at') or '', r['origin'], r['origin_source'],
               ('Y' if r.get('review_reason') else ''),
               r['origin'],                  # 故障分层 = origin
               ('已复现' if reproduced else '待复现'),  # 复现状态
               '', '', '', '', '', '', '', '']        # can-repro/why-not/script/desc/trigger/exc/raw/scope (fill below)
        if str(n) in ver:
            v = ver[str(n)]
            row[12] = '能复现'
            row[15] = v['root_desc']
            row[18] = v['raw'][:400]
            row[17] = v['channel']
            if n in code_src:
                row[14] = code_src[n][1]; row[16] = code_src[n][2]
        elif n in code_src and reproduced:
            desc, script, trigger = code_src[n]
            row[12] = '能复现'
            row[15] = desc; row[14] = script; row[16] = trigger
            row[18] = (prog.get(str(n), {}).get('message') or '')[:400]
            row[17] = 'see-raw'
        else:
            # not reproduced: record WHY (from repro_progress reason, or the tier classifier)
            pr = prog.get(str(n), {})
            if pr.get('status') == 'limited':
                row[12] = '不能复现'
                row[13] = pr.get('reason') or '复现受限（未捕获到缺陷）'
            else:
                row[12] = '待跑'
                row[13] = '未尝试复现'
        if reproduced:
            for col in range(1, len(headers)+1):
                ws.cell(row=i, column=col).fill = green
        ws.append(row)

    widths = [6, 12, 12, 45, 50, 8, 18, 12, 10, 8, 12, 10, 10, 50, 30, 40, 28, 14, 70, 12]
    for j, w in enumerate(widths, start=1):
        ws.column_dimensions[chr(64+j)].width = w
    wb.save(OUT)
    print('rows:', len(orig), '| reproduced:', sum(1 for r in orig if (str(r['number']) in ver or (r['number'] in rc.CASES and prog.get(str(r['number']),{}).get('defect_captured')))))
    print('->', OUT)


if __name__ == '__main__':
    main()