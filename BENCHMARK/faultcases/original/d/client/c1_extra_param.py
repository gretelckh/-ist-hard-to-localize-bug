"""Client报文层故障1：Client组装报文时多加了一个未定义参数"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def add(a: int, b: int) -> int:
        """两个数相加，只接受a和b"""
        return a + b

    async with Client(server) as client:
        try:
            # Client 错误：多传了一个未定义的参数 c
            # 变体修改指南（修改下一行多出来的第三个 key/value）：
            # 正常参数只有 {"a": 1, "b": 2}；当前多余参数是 "c": 999。
            # 三个可替换错误版本："debug": True、"timeout": 30、"user_id": 1。
            # 注意：SDK v2.0.0 默认忽略额外参数，这些版本可能仍然正常返回。
            result = await client.call_tool("add", {"a": 1, "b": 2, "user_id": 1})
            print(result)
        except Exception as e:
            print("=== 故障类型：Client报文层 - 多余未定义参数 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
