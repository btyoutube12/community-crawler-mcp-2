import os
from fastmcp import FastMCP

mcp = FastMCP("CommunityCrawler")

@mcp.tool()
def hello():
    return {
        "status": "success",
        "message": "MCP 연결 성공"
    }

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )