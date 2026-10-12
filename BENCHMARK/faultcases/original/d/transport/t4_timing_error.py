"""Transport传输层故障4-变体3：离开 Client 生命周期后再次调用工具"""
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
        # 正常进入 Client 生命周期
        async with client:
            res1 = await client.call_tool(
                "add",
                {"a": 1, "b": 2}
            )

            print("第一次调用成功：", res1)

        # 到这里已经离开 async with
        # __aexit__ 已经执行
        # Client 会话已经关闭

        # 错误：
        # 使用同一个已经退出生命周期的 client 再次调用工具
        res2 = await client.call_tool(
            "add",
            {"a": 3, "b": 4}
        )

        print(res2)

    except Exception as e:
        print("=== 故障类型：Transport传输层 - 离开上下文后再次 call_tool ===")
        print(f"异常类型: {type(e).__name__}")
        print(f"异常信息: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())