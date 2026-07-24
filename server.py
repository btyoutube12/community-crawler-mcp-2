import os
from fastmcp import FastMCP

mcp = FastMCP("CommunityCrawler")

@mcp.tool()
def hello():
    return {
        "status": "success",
        "message": "MCP 연결 성공"
    }

@mcp.tool()
def crawl_community(community: str):
    """
    지정된 커뮤니티의 데이터를 수집한다.
    """

    return {
        "community": community,
        "posts_collected": 0,
        "comments_collected": 0,
        "saved_to_firestore": False,
        "status": "success"
    }

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )