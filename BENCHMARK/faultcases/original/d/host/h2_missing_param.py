"""Host层故障2：LLM漏传必填参数 b"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def add(a: int, b: int) -> int:
        """两个数相加，a和b都是必填"""
        return a + b

    async with Client(server) as client:
        try:
            # Host 错误：只传了 a，漏了必填的 b
            # 变体修改指南（修改下一行的参数字典）：
            # 正常参数：{"a": 5, "b": 3}；当前错误值：{"a": 5}（缺 b）。
            # 三个可替换错误版本：{"b": 3}（缺 a）、{}（a/b 都缺）、
            # {"a": 10}（换一个输入但仍缺 b）。每次只选其中一个字典。
            result = await client.call_tool("add", {"a": 10})
            print(result)
        except Exception as e:
            print("=== 故障类型：Host调度层 - 缺少必填参数 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
