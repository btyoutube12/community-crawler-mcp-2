import os
from fastmcp import FastMCP
import json

import firebase_admin

from firebase_admin import credentials
from firebase_admin import firestore

mcp = FastMCP("CommunityCrawler")
firebase_credentials = json.loads(
    os.environ["FIREBASE_CREDENTIALS"]
)

cred = credentials.Certificate(
    firebase_credentials
)

firebase_admin.initialize_app(cred)

db = firestore.client()

@mcp.tool()
def save_test():
    """
    Firestore 저장 테스트
    """

    db.collection("community_posts").add({
        "community": "test",
        "board": "test",
        "title": "Firestore 연결 테스트",
        "content": "MCP 저장 성공",
        "url": "https://test.com"
    })

    return {
        "status": "success",
        "saved_to_firestore": True
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