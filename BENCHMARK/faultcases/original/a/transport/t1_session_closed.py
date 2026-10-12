"""Transport传输层故障1：会话中途关闭"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer()
    @server.tool()
    async def add(a: int, b: int) -> int:
        await asyncio.sleep(1)
        return a + b

    client = Client(server)
    try:
        await client.__aenter__()
        res1 = await client.call_tool("add", {"a": 1, "b": 2})
        print("首次调用成功：", res1)
        # 主动关闭会话
        # 变体修改指南（改变关闭动作相对调用的位置）：
        # 正常顺序：所有 call_tool 都在进入和退出会话之间完成。
        # 当前错误：首次调用后关闭，再次调用。
        # 三个错误版本：进入后立即关闭再首次调用；list_tools 后关闭再调用；
        # 改用 async with，离开代码块后复用同一个 client 调用。
        await client.__aexit__(None, None, None)
        # 关闭后再次调用
        res2 = await client.call_tool("add", {"a": 3, "b": 4})
        print(res2)
    except Exception as e:
        print("=== 故障类型：Transport传输层 - 会话中途关闭 ===")
        print(f"异常类型: {type(e).__name__}")
        print(f"异常信息: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
