"""Client报文层故障3：Client传了一个不在枚举范围内的值"""
import asyncio
import traceback
from enum import Enum
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

class Color(str, Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def set_color(color: Color) -> str:
        """设置颜色，只接受 red/green/blue"""
        return f"Color set to {color.value}"

    async with Client(server) as client:
        try:
            # Client 错误：传了 "yellow"，不在枚举范围内
            # 变体修改指南（修改下一行 color 的值）：
            # 合法值："red"、"green"、"blue"；当前错误值："yellow"。
            # 三个可替换错误版本："purple"、"RED"（大小写错误）、""（空值）。
            result = await client.call_tool("set_color", {"color": "purple"})
            print(result)
        except Exception as e:
            print("=== 故障类型：Client报文层 - 枚举值非法 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
