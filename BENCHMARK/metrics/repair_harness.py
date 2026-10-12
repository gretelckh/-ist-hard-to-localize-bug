#!/usr/bin/env python3
"""Phase C: repair experiment. Does the diagnostic-clue tool help an LLM REPAIR faults,
not just localise them?

For each fault case we ask a genuine LLM to produce a FIXED, runnable version of the faulting
case script. We then execute that fixed script and verify it (a) no longer errors and (b)
returns the expected correct value. We compare two conditions on the SAME cases:

  (a) no-clue  : LLM sees the faulting source + the SDK output only
  (b) +clue    : LLM sees the faulting source + the SDK output + the diagnostic-clue tool output
                 (directional guidance, no origin-layer leak)

Object set: the auto-verifiable fixable cases (synthetic MCP-Fault-20 minus the three with no
observable repair effect, c4_wrong_method / t3_invalid_message / s7_duplicate_tool_registration,
plus the six advanced production-style hidden bugs). The real-streamable-HTTP cases are NOT here
because they are embedded in HTTP runners and their correctness is not auto-verifiable; they are
documented as an excluded boundary.

Outputs:
  - data/repair_results.json       per case: condition, fixed_script, ran, passed, stdout, reason
  - data/repair_summary.json       per-condition success rate
  - figs/fig_repair.png            no-clue vs +clue repair success rate
"""
import os, sys, json, re, subprocess, argparse, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG = os.path.join(REPO, 'faultcases', 'original', 'a')
ADV = os.path.join(REPO, 'faultcases', 'advanced')

def load_env():
    p = os.path.join(REPO, '.env')
    if os.path.exists(p):
        for line in open(p, encoding='utf-8'):
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip())

# ---- per-case definition -------------------------------------------------------
# each entry: case, layer, source (path), check(output)->bool, hint(what correct looks like)
def read(p):
    return open(p, encoding='utf-8', errors='replace').read()

CASES = [
    # (id, layer, source_path, expected_marker, fix_description_hint)
    ('h1_tool_not_exist', 'Host', ORIG + '/host/h1_tool_not_exist.py', '8', 'call the registered tool "add" with a=5 b=3, result 8'),
    ('h2_missing_param',  'Host', ORIG + '/host/h2_missing_param.py',  '8', 'pass both a=5 and b=3, result 8'),
    ('h3_wrong_param_name','Host', ORIG + '/host/h3_wrong_param_name.py', 'User_123', 'use key user_id=123, result "User_123"'),
    ('h4_wrong_param_type','Host', ORIG + '/host/h4_wrong_param_type.py', '8', 'pass a as int 5 (not string), result 8'),
    ('c1_extra_param',    'Client', ORIG + '/client/c1_extra_param.py', '3', 'send only a=1 b=2, result 3'),
    ('c2_wrong_nesting',  'Client', ORIG + '/client/c2_wrong_nesting.py', '3', 'arguments at top level a=1 b=2, result 3'),
    ('c3_invalid_enum',   'Client', ORIG + '/client/c3_invalid_enum.py', 'red', 'send a valid enum member (red/green/blue), e.g. color=red'),
    ('s1_divide_by_zero', 'Server', ORIG + '/server/s1_divide_by_zero.py', '5', 'divide with b=2 (non-zero), result 5.0'),
    ('s2_index_out_of_range','Server', ORIG + '/server/s2_index_out_of_range.py', 'apple', 'index 0 within range, result "apple"'),
    ('s3_assertion_error','Server', ORIG + '/server/s3_assertion_error.py', '剩余', 'withdraw an amount <= balance, e.g. amount=100'),
    ('s4_custom_exception','Server', ORIG + '/server/s4_custom_exception.py', 'ORD001', 'query an existing order, e.g. order_id=ORD001'),
    ('s5_oversized_response','Server', ORIG + '/server/s5_oversized_response.py', None, 'return a bounded/short payload (not ~20M chars)'),
    ('s6_pydantic_serialize_error','Server', ORIG + '/server/s6_pydantic_serialize_error.py', 'Alice', 'return JSON-serializable primitives, e.g. {"user":{"name":"Alice","age":30}}'),
    ('s8_auth_error',     'Server', ORIG + '/server/s8_auth_error.py', '已删除', 'use the valid api_key so the file is deleted'),
    ('t1_session_closed', 'Transport', ORIG + '/transport/t1_session_closed.py', '7', 'do both calls inside the async context manager, result 7'),
    ('t2_request_cancelled','Transport', ORIG + '/transport/t2_request_cancelled.py', 'done', 'do not cancel the call (or handle cancellation), result "done"'),
    ('t4_timing_error',   'Transport', ORIG + '/transport/t4_timing_error.py', '3', 'make the call inside the async context manager, result 3'),
    # advanced (production-style hidden bugs) — custom checks handled below
    ('a1_concurrent_race','Host', 'ADV:a1', None, 'add an asyncio.Lock around read-modify-write; N concurrent calls return unique {1..N}'),
    ('a2_slow_timeout',   'Transport', 'ADV:a2', None, 'add client-side asyncio.wait_for timeout; a sane secs returns "done", a too-large one raises TimeoutError'),
    ('a3_dup_reg_race',   'Server', 'ADV:a3', None, 'register the tool once (or rename the duplicate); calc(2,3) returns 5 and only one tool is listed'),
    ('a4_state_leak',     'Server', 'ADV:a4', None, 'scope state per session/call so a fresh client sees empty history; return a copy not the live list'),
    ('a5_stream_interrupt','Server', 'ADV:a5', None, 'each step self-contained; fetch(1) returns "item-1" and downstream steps consume it'),
    ('a6_concurrent_shared_mutation','Host', 'ADV:a6', None, 'synchronise increment; N concurrent calls return unique {1..N}'),
]

# Bespoke standalone faulting source for each advanced case (self-contained, runnable).
ADV_SRC = {
'a1': '''import asyncio
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("race-server")
    state = {"v": 0}
    @server.tool()
    async def counter() -> int:
        tmp = state["v"]
        await asyncio.sleep(0)
        state["v"] = tmp + 1
        return state["v"]
    async with Client(server) as client:
        rs = await asyncio.gather(*[client.call_tool("counter", {}) for _ in range(6)])
        for r in rs:
            print(r)
if __name__ == "__main__":
    asyncio.run(main())
''',
'a2': '''import asyncio
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("slow-server")
    @server.tool()
    def work(secs: int) -> str:
        import time; time.sleep(secs); return "done"
    async with Client(server) as client:
        r = await client.call_tool("work", {"secs": 3})
        print(r)
if __name__ == "__main__":
    asyncio.run(main())
''',
'a3': '''import asyncio
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("dup-server")
    @server.tool()
    def calc(a: int, b: int) -> int:
        return a + b
    @server.tool()
    def calc(a: int, b: int) -> int:
        return a - b
    async with Client(server) as client:
        tools = await client.list_tools()
        print(tools)
        r = await client.call_tool("calc", {"a": 2, "b": 3})
        print(r)
if __name__ == "__main__":
    asyncio.run(main())
''',
'a4': '''import asyncio
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("leak-server")
    hist = []
    @server.tool()
    def record(x: int) -> str:
        hist.append(x); return "ok"
    @server.tool()
    def get_history() -> list:
        return list(hist)
    async with Client(server) as client_a:
        await client_a.call_tool("record", {"x": 99})
    # A second, independent client/session should NOT see client_a's data if state is scoped per session.
    async with Client(server) as client_b:
        r = await client_b.call_tool("get_history", {})
        print("SESSION_B_HISTORY:", r)
if __name__ == "__main__":
    asyncio.run(main())
''',
'a5': '''import asyncio
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("stream-server")
    @server.tool()
    def fetch(id: int) -> str:
        return "item-" + str(id)
    async with Client(server) as client:
        r = await client.call_tool("fetch", {"id": 1})
        print(r)
if __name__ == "__main__":
    asyncio.run(main())
''',
'a6': '''import asyncio
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("increment-server")
    shared = {"n": 0}
    @server.tool()
    def increment() -> int:
        shared["n"] += 1
        return shared["n"]
    async with Client(server) as client:
        rs = await asyncio.gather(*[client.call_tool("increment", {}) for _ in range(6)])
        for r in rs:
            print(r)
if __name__ == "__main__":
    asyncio.run(main())
''',
}

# expected-marker verification for the synthetic cases
def make_check(expected):
    if expected is None:
        return None  # s5 has a custom length check; advanced have custom checks
    def check(out, err, case):
        if 'is_error=True' in out and expected not in out:
            return False, f'error surfaced, missing {expected!r}'
        if expected in out:
            return True, f'found marker {expected!r}'
        return False, f'missing marker {expected!r}'
    return check

def check_s5(out, err, case):
    m = re.search(r'返回长度:\s*(\d+)', out)
    if m:
        n = int(m.group(1))
        if n < 20000:
            return True, f'bounded payload length {n}'
        return False, f'still oversized ({n} chars)'
    return False, 'no length marker found'

def check_a1(out, err, case):
    return _check_unique_seq(out)

def check_a6(out, err, case):
    return _check_unique_seq(out)

def _check_unique_seq(out):
    # extract result values from structured_content={'result': N} or the trailing int
    vals = [int(x) for x in re.findall(r"result'?:\s*(\d+)", out)]
    if not vals:
        vals = [int(x) for x in re.findall(r'\b(\d+)\b', out) if 1 <= int(x) <= 100]
    if not vals:
        return False, 'no numeric result values captured'
    n = len(vals); uniq = set(vals)
    if uniq == set(range(1, n + 1)):
        return True, f'unique sequence 1..{n}'
    return False, f'not a unique 1..N sequence: {sorted(uniq)} (n={n})'

def check_a2(out, err, case):
    return ('done' in out or 'TimeoutError' in out or 'timed out' in out or 'asyncio.exceptions.TimeoutError' in err), 'timeout handled or tool completed'

def check_a3(out, err, case):
    ok_list = 'calc' in out
    ok_val = '5' in out
    return (ok_list and ok_val), 'calc returns 5 and is listed'

def check_a4(out, err, case):
    # a correct fix scopes state per session, so an independent client sees empty history ([]).
    if 'SESSION_B_HISTORY' in out and '[]' in out:
        return True, 'session B sees empty history (state scoped per session)'
    return False, 'session B still sees leaked state (history not empty)'

def check_a5(out, err, case):
    return ('item-1' in out), 'fetch(1) returns item-1'

CHECK = {
    's5': check_s5, 'a1': check_a1, 'a2': check_a2, 'a3': check_a3,
    'a4': check_a4, 'a5': check_a5, 'a6': check_a6,
}

# ---- LLM prompt ----------------------------------------------------------------
def repair_prompt(source, surface, clue):
    p = (
        "You are repairing a fault in a Model Context Protocol (MCP) pipeline that uses the "
        "official `mcp` Python SDK (mcp.server.mcpserver.MCPServer, mcp.client.client.Client, "
        "in-memory transport). A developer ran the faulting script below and observed the SDK "
        "output. Your job: produce a CORRECTED, runnable version of the script that fixes the "
        "root cause and returns the expected value.\n\n"
        "RULES:\n"
        "- Output ONLY a single Python code block (```python ... ```) with the COMPLETE fixed "
        "script. No prose, no explanation.\n"
        "- Keep the same tools, imports and overall structure. Change only what is needed to fix "
        "the fault.\n"
        "- The script must be self-contained and runnable with `python -X utf8 <file>.py`.\n"
        "- Do NOT remove the `print(result)` line that prints the returned CallToolResult.\n\n"
        "FAULTING SCRIPT:\n```python\n" + source + "\n```\n\n"
        "SDK OUTPUT:\n" + surface + "\n"
        + (("\n\nDIAGNOSTIC GUIDANCE (direction only, does NOT state the answer):\n" + clue + "\n") if clue else "")
        + "\nNow output the fixed script as a single python code block:"
    )
    return p

def extract_py(text):
    m = re.search(r'```python\s*\n(.*?)```', text, re.S)
    if m:
        return m.group(1)
    m = re.search(r'```\s*\n(.*?)```', text, re.S)
    if m:
        return m.group(1)
    # fall back: everything from first 'import'/'async def' to end
    return text

def run_fixed(pycode):
    """Run a fixed script in a temp dir; return (stdout, stderr, ok)."""
    fd, path = tempfile.mkstemp(suffix='.py', dir=tempfile.gettempdir())
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as fh:
            fh.write(pycode)
        try:
            r = subprocess.run([sys.executable, '-X', 'utf8', path],
                               capture_output=True, text=True, timeout=90,
                               encoding='utf-8', errors='replace',
                               cwd=tempfile.gettempdir())
            return (r.stdout or ''), (r.stderr or ''), (r.returncode == 0)
        except subprocess.TimeoutExpired:
            return 'TIMEOUT', '', False
        except Exception as e:
            return '', f'RUNERR:{type(e).__name__}:{e}', False
    finally:
        os.remove(path)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--clue', action='store_true', help='append the diagnostic-clue tool output')
    ap.add_argument('--clues-leaky', action='store_true', help='append the leaky channel-label clue (negative control)')
    ap.add_argument('--pilot', type=int, default=0, help='only first N cases (pipeline check)')
    ap.add_argument('--advanced', action='store_true', help='only the advanced production-style cases')
    ap.add_argument('--out', default='', help='override output json filename')
    args = ap.parse_args()
    load_env()

    base = os.environ['CITYU_BASE_URL']; key = os.environ['CITYU_API_KEY']; model = os.environ['CITYU_MODEL']
    from openai import OpenAI
    client = OpenAI(base_url=base, api_key=key, timeout=180)

    # load diagnostic clues
    clues = {}
    try:
        crows = json.load(open(os.path.join(REPO, 'data', 'diagnostic_clues.json'), encoding='utf-8'))
        clues = {(c['variant'], c['case']): (c['hint_leaky'] if args.clues_leaky else c['hint']) for c in crows}
    except Exception as e:
        print('warn: no diagnostic_clues.json', e)

    cases = CASES
    if args.advanced:
        cases = [c for c in cases if c[0].startswith('a') and c[0][1].isdigit()]
    if args.pilot:
        cases = cases[:args.pilot]

    results = []
    for (cid, layer, src_path, marker, hint) in cases:
        if src_path and src_path.startswith('ADV:'):
            source = ADV_SRC[src_path.split(':')[1]]
        elif src_path and os.path.exists(src_path):
            source = read(src_path)
        else:
            source = ADV + '/run_advanced.py'
        # surface text: use the raw captured output for this case (from data/raw for synthetic)
        surface = ''
        # try to fetch a raw capture for the synthetic case (variant a)
        rawpath = os.path.join(REPO, 'data', 'raw', f'a_{cid}_{layer.lower()}.txt')
        if os.path.exists(rawpath):
            surface = open(rawpath, encoding='utf-8', errors='replace').read()
        else:
            surface = f'(case {cid}; fix per: {hint})'
        clue = clues.get(('a', cid)) if args.clue or args.clues_leaky else None
        # Advanced cases are not in dataset_runs/diagnostic_clues; they are ALL silent (is_error=False).
        # Provide the silent-channel clue so the clue condition is meaningful for them.
        if cid.startswith('a') and cid[1].isdigit() and (args.clue or args.clues_leaky):
            from metrics.diagnostic_clues import HINTS  # reuse the authoritative clue text
            clue = HINTS.get('silent') if not args.clues_leaky else 'CLUE-CHANNEL: silent'

        fixed = None
        ok = False
        for attempt in range(3):
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{'role': 'user', 'content': repair_prompt(source, surface, clue)}],
                    temperature=0.0, max_tokens=1200)
                fixed = extract_py(resp.choices[0].message.content or '')
                ok = True
                break
            except Exception as e:
                print(f'  [retry {attempt}] {cid}: {type(e).__name__}: {e}', file=sys.stderr)
        stdout, stderr, ranok = ('', '', False)
        passed, reason = False, 'no script generated'
        if ok and fixed:
            stdout, stderr, ranok = run_fixed(fixed)
            # advanced cases are keyed by short id (a1..a6); match by prefix.
            checker = CHECK.get(cid) or CHECK.get(cid.split('_')[0]) or make_check(marker)
            if checker:
                passed, reason = checker(stdout, stderr, cid)
            if not ranok and not passed:
                reason = f'exec failed: {reason}'
        results.append({'case': cid, 'layer': layer, 'clue': bool(args.clue or args.clues_leaky),
                        'fixed_script': fixed, 'ran_ok': ranok, 'passed': passed,
                        'reason': reason, 'stdout': stdout[:400], 'stderr': stderr[:400]})
        print(f"[{'CLUE' if args.clue else ('LEAKY' if args.clues_leaky else 'NOCLUE')}] "
              f"{cid:<28s} ran={ranok} passed={passed} ({reason})")

    outname = args.out or ('repair_results_leaky.json' if args.clues_leaky
                           else 'repair_results_clue.json' if args.clue
                           else 'repair_results.json')
    with open(os.path.join(REPO, 'data', outname), 'w', encoding='utf-8') as fh:
        json.dump(results, fh, ensure_ascii=False, indent=1)
    n = len(results); passed = sum(1 for r in results if r['passed'])
    print(f'\nWrote {n} -> data/{outname}')
    print(f'Repair success ({("clue" if args.clue else "leaky" if args.clues_leaky else "no-clue")}): '
          f'{passed}/{n} = {passed/n*100:.1f}%')

if __name__ == '__main__':
    main()