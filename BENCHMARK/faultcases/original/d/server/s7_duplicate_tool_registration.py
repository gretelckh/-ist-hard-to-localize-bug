"""Server工具层故障7：同一个工具名重复注册"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def calculate() -> str:
        """获取信息 - 版本1"""
        return "Version 1"

    try:
        # Server 错误：用同一个名字再注册一次
        # 变体修改指南（两个注册函数必须使用相同名称）：
        # 正常做法：第二个函数改成唯一名称，例如 get_info_v2。
        # 当前重复名称对：get_info/get_info；三个重复版本可分别把两个 def
        # 同时改成 status/status、search/search、calculate/calculate。
        # SDK v2.0.0 只给 WARNING 并保留第一次注册，不一定抛异常。
        @server.tool()
        def calculate() -> str:
            """获取信息 - 版本2"""
            return "Version 2"
    except Exception as e:
        print("=== 故障类型：Server工具层 - 工具重复注册 ===")
        print(f"异常类型: {type(e).__name__}")
        print(f"异常信息: {e}")
        print("=== 完整堆栈 ===")
        traceback.print_exc()
        return

    # 如果没报错，尝试调用看看返回哪个版本
    async with Client(server) as client:
        tools = await client.list_tools()
        print(f"工具列表: {[t.name for t in tools.tools]}")
        result = await client.call_tool("get_info", {})
        print(f"调用结果: {result}")

if __name__ == "__main__":
    asyncio.run(main())
