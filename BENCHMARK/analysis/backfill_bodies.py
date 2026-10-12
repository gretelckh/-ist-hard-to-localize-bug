"""Backfill full issue bodies for the 398 confirmed bugs (data-rebuild step 0).

The 398 confirmed bugs were screened from a pool where only the recently-pulled
issues (#2803+) have a full body; the older issues (#2-2802) only have a 300-char
body_head. This script merges the full body from the local snapshot
(C:\\Users\\KEHUIC~1\\AppData\\Local\\Temp\\opencode\\ist_work\\all_issues.json, which holds
the complete body for the 1,143 older issues) back into the pool, and flags any
confirmed bug whose body is still missing (those would need a fresh GitHub API call).

Run from MCP-Fault-Benchmark/:
    python analysis/backfill_bodies.py
"""
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
POOL = os.path.normpath(os.path.join(HERE, '..', 'data', 'full_pool', 'full_pool_screened.json'))
VERDICT = os.path.normpath(os.path.join(HERE, '..', 'data', 'full_pool', 'bug_review_verdicts.json'))
TEMP = r'C:\Users\KEHUIC~1\AppData\Local\Temp\opencode\ist_work\all_issues.json'
OUT = os.path.normpath(os.path.join(HERE, '..', 'data', 'full_pool', 'full_pool_screened.json'))


def main():
    pool = json.load(open(POOL, encoding='utf-8'))
    verdicts = json.load(open(VERDICT, encoding='utf-8'))['verdicts']
    conf_nums = [int(n) for n, d in verdicts.items() if d['verdict'] == 'BUG']

    # load local body snapshot for the older issues
    old_body = {}
    if os.path.exists(TEMP):
        a = json.load(open(TEMP, encoding='utf-8'))
        old_body = {x['number']: (x.get('body') or '') for x in a}
        print('local body snapshot (all_issues.json):', len(old_body), 'issues')

    by_num = {x['number']: x for x in pool}
    added = 0
    for n in conf_nums:
        rec = by_num.get(n)
        if not rec:
            continue
        if rec.get('body'):
            continue
        if n in old_body and old_body[n]:
            rec['body'] = old_body[n]
            added += 1

    json.dump(pool, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('backfilled body for', added, 'issues')
    print('confirmed total:', len(conf_nums))

    # report still-missing
    missing = [n for n in conf_nums if not (by_num[n].get('body') if by_num.get(n) else None)]
    print('still missing body:', len(missing), missing)


if __name__ == '__main__':
    main()