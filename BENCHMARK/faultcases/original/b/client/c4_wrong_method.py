"""Client报文层故障4：JSON-RPC方法名错误（v2高层Client封装不可篡改method，仅模拟说明）"""
import asyncio
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")
    @server.tool()
    def add(a: int, b: int) -> int:
        return a + b

    print("=== 故障类型：Client报文层 - 协议方法名错误 ===")
    # 变体修改指南（只能在底层原始 JSON-RPC method 字段中修改）：
    # 正常 method："tools/call"；当前说明中的错误值："tool/call"。
    # 三个错误版本："tools_call"、"tools/calls"、"tool.call"。
    # 本脚本的高层 Client 没有可修改的 method 字段；改下面的工具名不等价。
    print("【重要说明】MCP v2官方高层Client内置固定method='tools/call'，上层API无法手动传入错误method如'tools_call'；")
    print("该故障仅底层原始JSON-RPC发送场景可复现，本SDK封装后屏蔽此故障触发路径。")
    async with Client(server) as client:
        res = await client.call_tool("add", {"a":1,"b":2})
        print("正常返回：", res)

if __name__ == "__main__":
    asyncio.run(main())
