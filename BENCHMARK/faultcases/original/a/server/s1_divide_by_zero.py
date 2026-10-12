"""Server工具层故障1：工具内部除零运算崩溃"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def divide(a: int, b: int) -> float:
        """除法运算"""
        # Server 错误：b=0 时触发除零异常
        return a / b

    async with Client(server) as client:
        try:
            # 变体修改指南（修改下一行 a/b，但始终让 b=0）：
            # 正常示例：{"a": 10, "b": 2}；当前错误值：{"a": 10, "b": 0}。
            # 三个错误版本：{"a": 1, "b": 0}、{"a": -10, "b": 0}、
            # {"a": 0, "b": 0}。三者都会在 return a / b 处触发除零。
            result = await client.call_tool("divide", {"a": 10, "b": 0})
            print(result)
        except Exception as e:
            print("=== 故障类型：Server工具层 - 除零异常 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
