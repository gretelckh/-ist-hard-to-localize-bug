import asyncio
import traceback
from mcp.server.mcpserver import MCPServer
from mcp.client.client import Client

async def main():
    server = MCPServer("demo-server")

    @server.tool()
    def delete_file(file_path: str, api_key: str) -> str:
        """删除文件，需要API密钥"""
        # Server 错误：模拟鉴权失败
        valid_key = "sk-valid-12345"
        if api_key != valid_key:
            raise PermissionError(f"鉴权失败，API密钥无效: {api_key}")
        return f"文件 {file_path} 已删除"

    async with Client(server) as client:
        try:
            # 传入错误的 API 密钥
            # 变体修改指南（修改下面参数字典中的 api_key）：
            # 正常值："sk-valid-12345"；当前错误值："sk-wrong-key"。
            # 三个错误版本："sk-expired-key"、""（空字符串）、
            # "SK-VALID-12345"（大小写不匹配）。
            result = await client.call_tool(
                "delete_file",
                {"file_path": "/tmp/test.txt", "api_key": "ssk-expired-key"}
            )
            print(result)
        except Exception as e:
            print("=== 故障类型：Server工具层 - 鉴权权限失败 ===")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常信息: {e}")
            print("=== 完整堆栈 ===")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
