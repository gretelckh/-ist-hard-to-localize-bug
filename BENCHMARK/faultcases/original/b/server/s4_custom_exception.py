"""Server工具层故障4：工具抛出自定义业务异常"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

class OrderNotFoundError(Exception):
    """自定义异常：订单不存在"""
    pass

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def get_order(order_id: str) -> str:
        """查询订单"""
        valid_orders = {"ORD001", "ORD002"}
        if order_id not in valid_orders:
            # Server 错误：抛出自定义业务异常
            raise OrderNotFoundError(f"订单 {order_id} 不存在")
        return f"订单 {order_id} 详情: ..."

    async with Client(server) as client:
        try:
            # 变体修改指南（修改下一行 order_id 的值）：
            # 合法值："ORD001"、"ORD002"；当前错误值："ORD999"。
            # 三个错误版本："ORD000"、"ord001"（大小写错误）、""（空订单号）。
            result = await client.call_tool("get_order", {"order_id": "ORD000"})
            print(result)
        except Exception as e:
            print("=== 故障类型：Server工具层 - 自定义业务异常 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
