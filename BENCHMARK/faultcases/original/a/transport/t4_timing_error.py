"""Transport传输层故障4：初始化时序错误，未握手直接调用工具"""
import asyncio
import traceback
from mcp import Client
from mcp.server.mcpserver import MCPServer

async def main():
    server = MCPServer("demo-server")
    @server.tool()
    def add(a:int,b:int) -> int:
        return a+b
    client = Client(server)
    try:
        # 未执行async with/await __aenter__初始化握手，直接调用
        # 变体修改指南（修改“未进入/已离开 Client 生命周期时执行的操作”）：
        # 正常做法：在 async with Client(server) as client: 内调用。
        # 当前错误：进入上下文前 call_tool；三个错误版本：进入前 list_tools、
        # 进入前访问 client.session、离开 async with 后再次 call_tool。
        res = await client.call_tool("add",{"a":1,"b":2})
        print(res)
    except Exception as e:
        print("=== 故障类型：Transport传输层 - 初始化时序错误 ===")
        print(f"异常类型: {type(e).__name__}")
        print(f"异常信息: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
