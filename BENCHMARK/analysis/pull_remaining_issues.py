"""Pull the remaining recent issues (#2803-#3656) from modelcontextprotocol/python-sdk.

Uses the GitHub REST API /issues endpoint (state=all) paginated, filters to pure
issues (no `pull_request` key), keeps full body, and merges with the existing
full_pool_screened.json so the pool covers all 1,343 pure issues.

NOTE: GitHub core rate limit is 60/hr unauthenticated. This script respects it
by stopping on 403 and printing how many it fetched. Rerun after rate limit
resets to continue.

Run from MCP-Fault-Benchmark/:
    python analysis/pull_remaining_issues.py
"""
import urllib.request, json, time, os, sys
sys.stdout.reconfigure(encoding='utf-8')

REPO = 'modelcontextprotocol/python-sdk'
BASE = f'https://api.github.com/repos/{REPO}/issues'
POOL = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'full_pool', 'full_pool_screened.json')
POOL = os.path.normpath(POOL)


def gh(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'opencode', 'Accept': 'application/vnd.github+json'})
    return json.load(urllib.request.urlopen(req, timeout=40))


def main():
    existing = json.load(open(POOL, encoding='utf-8'))
    have = {x['number'] for x in existing}
    print(f'existing pool: {len(existing)} issues (max num {max(have)})')

    new_records = []
    seen = set()
    # Paginate from the newest; we only care about issue numbers above what we have.
    # Per_page=100, state=all. Stop when a page is entirely <= existing max.
    page = 1
    while True:
        url = f'{BASE}?state=all&per_page=100&page={page}&sort=created&order=desc'
        try:
            items = gh(url)
        except Exception as e:
            print('ERR on page', page, e)
            break
        if not items:
            print('empty page', page, '-> done')
            break
        print(f'page {page}: {len(items)} raw')
        any_new = False
        for i in items:
            num = i['number']
            if num in seen:
                continue
            seen.add(num)
            if num in have:
                continue
            if 'pull_request' in i:
                continue
            any_new = True
            new_records.append({
                'number': num,
                'title': i['title'],
                'state': i['state'],
                'created_at': i.get('created_at', ''),
                'label': '',  # filled later by screening
                'url': i['html_url'],
                'body_head': (i.get('body') or '')[:300],
                'body': i.get('body') or '',
            })
        # Stop if the newest items on this page are all <= max(have) (we've caught up)
        page_max = max((i['number'] for i in items), default=0)
        if page_max <= max(have):
            print('caught up: page max', page_max, '<=', max(have))
            break
        if not any_new and page_max > max(have):
            # still catching up through PRs; continue
            pass
        if len(items) < 100:
            break
        page += 1
        time.sleep(0.5)

    print('new pure issues fetched:', len(new_records))
    if new_records:
        # Save raw for later merge (don't overwrite pool until screened)
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'full_pool', '_remaining_raw.json')
        out = os.path.normpath(out)
        json.dump(new_records, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('saved ->', out)
    # print the target reproducible bugs presence
    target = set(range(3549, 3647))
    got = {x['number'] for x in new_records}
    missing_target = sorted(target - got)
    print('target #3549-#3646 present in new:', len(target & got), 'still missing:', missing_target)


if __name__ == '__main__':
    main()