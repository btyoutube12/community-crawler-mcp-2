import os
import json

from fastmcp import FastMCP
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


# ==========================================
# MCP 초기화
# ==========================================

mcp = FastMCP("CommunityCrawler")


# ==========================================
# Firestore 초기화
# ==========================================

firebase_credentials = json.loads(
    os.environ["FIREBASE_CREDENTIALS"]
)

cred = credentials.Certificate(firebase_credentials)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()


# ==========================================
# 저장 함수
# ==========================================

def save_post(post):

    db.collection("community_posts").add({
        "community": post["community"],
        "board": post["board"],
        "title": post["title"],
        "content": post["content"],
        "url": post["url"],
        "created_at": post["created_at"],
        "crawled_at": firestore.SERVER_TIMESTAMP
    })


# ==========================================
# 테스트
# ==========================================

@mcp.tool()
def save_test():

    try:

        save_post({
            "community": "test",
            "board": "test",
            "title": "Firestore 연결 테스트",
            "content": "MCP 저장 성공",
            "url": "https://test.com",
            "created_at": None
        })

        return {
            "status": "success",
            "saved_to_firestore": True
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }


# ==========================================
# 크롤러 자리
# ==========================================

@mcp.tool()
def crawl_dcinside():

    try:

        sample_posts = []

        for i in range(1, 6):

            sample_posts.append({
                "community": "디시인사이드",
                "board": "dcbest",
                "title": f"샘플 게시글 {i}",
                "content": f"테스트 데이터 {i}",
                "url": f"https://example.com/{i}",
                "created_at": None
            })

        for post in sample_posts:
            save_post(post)

        return {
            "community": "디시인사이드",
            "posts_collected": len(sample_posts),
            "comments_collected": 0,
            "saved_to_firestore": True,
            "status": "success"
        }

    except Exception as e:

        return {
            "community": "디시인사이드",
            "saved_to_firestore": False,
            "status": "error",
            "message": str(e)
        }


# ==========================================
# 지원 커뮤니티
# ==========================================

SUPPORTED_COMMUNITIES = {
    "디시인사이드": crawl_dcinside,
}


# ==========================================
# MCP Tool
# ==========================================

@mcp.tool()
def crawl_community(community: str):

    aliases = {
        "dcinside": "디시인사이드",
        "dc": "디시인사이드",
        "디씨": "디시인사이드"
    }

    community = aliases.get(
        community.lower(),
        community
    )

    if community not in SUPPORTED_COMMUNITIES:

        return {
            "community": community,
            "status": "unsupported_community",
            "saved_to_firestore": False
        }

    return SUPPORTED_COMMUNITIES[community]()


# ==========================================
# 실행
# ==========================================

if __name__ == "__main__":

    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )