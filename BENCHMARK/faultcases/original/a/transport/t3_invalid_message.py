"""Transport传输层故障3：非法原始消息（v2高层无原始报文发送接口，仅说明）"""
import asyncio
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")
    @server.tool()
    def add(a:int,b:int) -> int:
        return a+b
    print("=== 故障类型：Transport传输层 - 非法消息载荷 ===")
    # 变体修改指南（只能在底层传输流的原始 bytes 写入位置修改）：
    # 正常载荷是完整 UTF-8 JSON-RPC；三个错误版本：b"not-json"、
    # b'{"jsonrpc":"2.0"'（JSON 不完整）、b"\xff\xfe"（非法 UTF-8）。
    # 本脚本使用高层 Client，没有原始 bytes 写入点；改 call_tool 参数不等价。
    print("【说明】v2高层Client封装全部JSON-RPC序列化逻辑，上层无法手动写入非法原始字符串报文；")
    print("该故障仅底层传输流直接写数据场景可触发，本高层脚本无法复现。")
    async with Client(server) as client:
        print(await client.call_tool("add",{"a":1,"b":2}))

if __name__ == "__main__":
    asyncio.run(main())
