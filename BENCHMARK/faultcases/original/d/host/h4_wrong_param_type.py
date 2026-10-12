"""Host层故障4：LLM把int参数传成了字符串"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def add(a: int, b: int) -> int:
        """两个数相加"""
        return a + b

    async with Client(server) as client:
        try:
            # Host 错误：a 应该是 int，传成了字符串 "5"
            # 变体修改指南（修改下一行参数 a 的值）：
            # 正常类型和值：5（int）；当前错误值："5"（str）。
            # 注意：SDK v2.0.0 会把 "5" 自动转成 5，所以当前版本不会报错。
            # 三个更可靠的错误版本："five"、[5]、None；它们通常无法转成 int。
            result = await client.call_tool("add", {"a": None, "b": 3})
            print(result)
        except Exception as e:
            print("=== 故障类型：Host调度层 - 参数类型错误 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
