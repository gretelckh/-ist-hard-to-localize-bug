"""Transport传输层故障4-变体1：未进入 Client 生命周期就 list_tools"""
import asyncio
import traceback
from mcp import Client
from mcp.server.mcpserver import MCPServer


async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def add(a: int, b: int) -> int:
        return a + b

    client = Client(server)

    try:
        # 错误：
        # Client 只是创建了对象，
        # 但还没有通过 async with / __aenter__ 进入会话
        # 就直接请求工具列表
        tools = await client.list_tools()

        print(tools)

    except Exception as e:
        print("=== 故障类型：Transport传输层 - 初始化前 list_tools ===")
        print(f"异常类型: {type(e).__name__}")
        print(f"异常信息: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())