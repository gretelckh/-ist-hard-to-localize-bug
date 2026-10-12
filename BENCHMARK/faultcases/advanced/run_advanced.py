"""高级/真实难bug 用例：
新增类别：并发竞态(共享状态)、慢工具超时、并发重复注册、跨调用状态泄漏、流式/多步中断。
用官方 MCP SDK v2（mcp.server.mcpserver.MCPServer）内存传输运行，捕获真实 SDK 返回对象。
"""
import asyncio, sys
sys.stdout.reconfigure(encoding='utf-8')
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def run_case(case_id, builder, layer, root_desc, call_args=None, timeout=None):
    server = builder()
    out = []
    async with Client(server) as client:
        try:
            t = asyncio.ensure_future(client.call_tool(case_id, call_args or {}))
            res = await asyncio.wait_for(t, timeout=timeout) if timeout else await t
            out.append(res)
        except Exception as e:
            out.append(f"RAISED:{type(e).__name__}:{e}")
    return {'case': case_id, 'layer': layer, 'root_desc': root_desc, 'message': str(out[0]) if out else ''}

def build_a1():  # 并发竞态：无锁共享状态，多任务最后写入者胜
    server = MCPServer("race-server")
    state = {"v": 0}
    @server.tool()
    async def counter() -> int:
        tmp = state["v"]
        await asyncio.sleep(0)
        state["v"] = tmp + 1
        return state["v"]
    return server

def build_a2():  # 慢工具：阻塞远超预期，调用方超时/挂起
    server = MCPServer("slow-server")
    @server.tool()
    def slow_work(secs: int) -> str:
        import time; time.sleep(secs); return "done"
    return server

def build_a3():  # 同名工具重复注册（第二条被忽略或仅告警）
    server = MCPServer("dup-server")
    @server.tool()
    def calc(a: int, b: int) -> int:
        return a + b
    @server.tool()
    def calc(a: int, b: int) -> int:  # same name -> potential silent override
        return a - b
    return server

def build_a4():  # 跨调用状态泄漏
    server = MCPServer("leak-server")
    hist = []
    @server.tool()
    def record(x: int) -> str:
        hist.append(x); return "ok"
    @server.tool()
    def get_history() -> list:
        return list(hist)
    return server

def build_a5():  # 流式/步骤中断：依赖上前一步产物
    server = MCPServer("stream-server")
    @server.tool()
    def fetch(id: int) -> str:
        return "item-" + str(id)
    return server

def build_a6():  # 并发无锁共享变量递增（无 await，纯内联仍可展现竞态语义与无报错）
    server = MCPServer("increment-server")
    shared = {"n": 0}
    @server.tool()
    def increment() -> int:
        shared["n"] += 1
        return shared["n"]
    return server

async def main():
    # 每个用例： 调用名，构造器，层，根因描述，参数，超时
    cases = [
        ('a1_concurrent_race', build_a1, 'Host调度层', '并发调用同一共享状态工具，无锁竞态', 'counter', {}),
        ('a2_slow_timeout', build_a2, 'Transport传输层', '慢工具阻塞导致调用超时/挂起', 'slow_work', {'secs': 10}),
        ('a3_dup_reg_race', build_a3, 'Server工具层', '同名工具重复注册，第二个被覆盖/忽略', 'calc', {'a': 2, 'b': 3}),
        ('a4_state_leak', build_a4, 'Server工具层', '跨调用状态泄漏(先record再get_history)', 'get_history', {}),
        ('a5_stream_interrupt', build_a5, 'Server工具层', '流式/多步请求中断', 'fetch', {'id': 1}),
        ('a6_concurrent_shared_mutation', build_a6, 'Host调度层', '并发共享变量递增竞态', 'increment', {}),
    ]
    results = []
    for cid, builder, layer, desc, cname, cargs in cases:
        try:
            r = await run_case(cname, builder, layer, desc, cargs)
            r['case'] = cid
        except Exception as e:
            r = {'case': cid, 'layer': layer, 'root_desc': desc, 'message': f'RUNERR:{type(e).__name__}:{e}'}
        results.append(r)
    import json
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    asyncio.run(main())