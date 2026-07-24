import os
import json
from fastmcp import FastMCP
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

==================================================
MCP 초기화
==================================================
mcp = FastMCP("CommunityCrawler")

==================================================
Firestore 초기화
==================================================
firebase_credentials = json.loads(
os.environ["FIREBASE_CREDENTIALS"]
)
cred = credentials.Certificate(firebase_credentials)
if not firebase_admin._apps:
firebase_admin.initialize_app(cred)
db = firestore.client()

==================================================
Firestore 저장 함수
==================================================
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
def save_comment(comment):
db.collection("community_comments").add({
"community": comment["community"],
"content": comment["content"],
"post_url": comment["post_url"],
"created_at": comment["created_at"],
"crawled_at": firestore.SERVER_TIMESTAMP
})

==================================================
테스트용
==================================================
@mcp.tool()
def save_test():
try:
save_post({
"community": "test",
"board": "test",
"title": "Firestore 연결 테스트",
"content": "MCP 저장 성공",
"url": "https://test.com ",
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

==================================================
커뮤니티 수집기
==================================================
def crawl_dcinside():
return {
"community": "디시인사이드",
"posts_collected": 0,
"comments_collected": 0,
"saved_to_firestore": False,
"status": "ready"
}
def crawl_fmkorea():
return {
"community": "에펨코리아",
"posts_collected": 0,
"comments_collected": 0,
"saved_to_firestore": False,
"status": "ready"
}
def crawl_ruliweb():
return {
"community": "루리웹",
"posts_collected": 0,
"comments_collected": 0,
"saved_to_firestore": False,
"status": "ready"
}
def crawl_inven():
return {
"community": "인벤",
"posts_collected": 0,
"comments_collected": 0,
"saved_to_firestore": False,
"status": "ready"
}
def crawl_mansidae():
return {
"community": "남성시대",
"posts_collected": 0,
"comments_collected": 0,
"saved_to_firestore": False,
"status": "ready"
}
def crawl_womansidae():
return {
"community": "여성시대",
"posts_collected": 0,
"comments_collected": 0,
"saved_to_firestore": False,
"status": "ready"
}

==================================================
지원 커뮤니티
==================================================
SUPPORTED_COMMUNITIES = {
"디시인사이드": crawl_dcinside,
"에펨코리아": crawl_fmkorea,
"루리웹": crawl_ruliweb,
"인벤": crawl_inven,
"남성시대": crawl_mansidae,
"여성시대": crawl_womansidae
}

==================================================
메인 MCP Tool
==================================================
@mcp.tool()
def crawl_community(community: str):
if community not in SUPPORTED_COMMUNITIES:
return {
"community": community,
"status": "unsupported_community",
"saved_to_firestore": False
}
return SUPPORTED_COMMUNITIEScommunity

==================================================
실행
==================================================
if name == "main":
mcp.run(
transport="streamable-http",
host="0.0.0.0",
port=int(os.environ.get("PORT", 8000))
)