"""Server工具层故障5：工具返回超大文本，JSON载荷膨胀"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def generate_huge_text() -> str:
        """生成超大文本"""
        # Server 错误：返回 1000 万字符的超大文本
        # 变体修改指南（修改下一行乘数）：
        # 正常小响应可用 1_000；当前压力值：10_000_000。
        # 三个递增版本：15_000_000、25_000_000、50_000_000。
        # 注意：in-memory 没有固定载荷上限，增大后仍可能成功；请逐级测试，
        # 不要一次设置过大，以免占用过多内存导致系统变慢。
        return "x" * 25_000_000

    async with Client(server) as client:
        try:
            result = await client.call_tool("generate_huge_text", {})
            print(f"返回长度: {len(str(result))}")
        except Exception as e:
            print("=== 故障类型：Server工具层 - 返回超大文本 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {str(e)[:500]}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
