"""验证：慢工具真实触发超时；以及状态泄漏的两次调用对照；并发竞态多任务对照。
目标：为新增的'真实难bug'提供确凿、可复现的证据。
"""
import asyncio, sys, json
sys.stdout.reconfigure(encoding='utf-8')
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

def build_slow(secs):
    s = MCPServer("slow-server")
    @s.tool()
    def work(secs: int) -> str:
        import time; time.sleep(secs); return "done"
    return s

def build_leak():
    s = MCPServer("leak-server"); hist = []
    @s.tool()
    def record(x: int) -> str: hist.append(x); return "ok"
    @s.tool()
    def get_history() -> list: return list(hist)
    return s

def build_race():
    s = MCPServer("race-server"); 
    @s.tool()
    async def counter() -> int:
        tmp = 0
        await asyncio.sleep(0)
        return tmp + 1
    return s

async def main():
    res = {}
    # 1) 超时验证：wait_for 1 秒，工具 sleep 5 秒 -> 应超时
    try:
        async with Client(build_slow(5)) as c:
            await asyncio.wait_for(c.call_tool("work", {"secs": 3}), timeout=1.0)
            res['timeout'] = 'NO-TIMEOUT(completed)'
    except asyncio.TimeoutError:
        res['timeout'] = 'TIMEOUT-RAISED (asyncio.TimeoutError)'
    except Exception as e:
        res['timeout'] = f'OTHER:{type(e).__name__}:{e}'

    # 2) 状态泄漏：末尾 record(99) 后 get_history 是否含它
    try:
        async with Client(build_leak()) as c:
            r1 = await c.call_tool("get_history", {})
            await c.call_tool("record", {"x": 99})
            r2 = await c.call_tool("get_history", {})
            res['state_leak_before'] = str(r1)
            res['state_leak_after'] = str(r2)
    except Exception as e:
        res['state_leak'] = f'ERR:{type(e).__name__}:{e}'

    # 3) 并发竞态：同时发 3 个 counter，看是否全部成功/有静默
    try:
        async with Client(build_race()) as c:
            rs = await asyncio.gather(*[c.call_tool("counter", {}) for _ in range(5)])
            res['concurrent_results'] = [str(x)[:60] for x in rs]
    except Exception as e:
        res['concurrent'] = f'ERR:{type(e).__name__}:{e}'

    print(json.dumps(res, ensure_ascii=False, indent=2))

asyncio.run(main())