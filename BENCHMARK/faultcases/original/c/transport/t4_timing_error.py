"""Transport传输层故障4-变体2：未进入 Client 生命周期就访问 session"""
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
        # Client 尚未进入 async context
        # 此时 session 还没有建立
        session = client.session

        print(session)

    except Exception as e:
        print("=== 故障类型：Transport传输层 - 初始化前访问 session ===")
        print(f"异常类型: {type(e).__name__}")
        print(f"异常信息: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())