"""Transport传输层故障2：请求中途取消"""
import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def slow_tool():
    await asyncio.sleep(5)
    return "done"

async def main():
    server = MCPServer("demo-server")
    server.tool()(slow_tool)
    async with Client(server) as client:
        task = asyncio.create_task(client.call_tool("slow_tool",{}))
        # 变体修改指南（修改下一行取消前等待时间，slow_tool 总时长为 5 秒）：
        # 正常情况：不调用 task.cancel()，直接 await task；当前错误值：0.5 秒后取消。
        # 三个错误版本：等待 0 秒、1 秒、4.5 秒后取消。
        # 等待时间必须小于 5 秒，否则工具可能已经完成，无法触发取消。
        await asyncio.sleep(4.5)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError as e:
            print("=== 故障类型：Transport传输层 - 请求中途取消 ===")
            print("异常类型: CancelledError")
            print("异常信息：工具请求执行中被主动取消")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
