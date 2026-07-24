import os
import json
import time
import random

import requests
from bs4 import BeautifulSoup

from fastmcp import FastMCP
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# ─────────────────────────────
# 초기 설정
# ─────────────────────────────
mcp = FastMCP("CommunityCrawler")

firebase_credentials = json.loads(os.environ["FIREBASE_CREDENTIALS"])
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred)
db = firestore.client()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://gall.dcinside.com/",
}

DC_LIST_URL = "https://gall.dcinside.com/board/lists/"
DC_VIEW_URL = "https://gall.dcinside.com/board/view/"


# ─────────────────────────────
# 디시인사이드 크롤링 함수
# ─────────────────────────────
def get_dc_list_page(gallery_id: str, page: int, list_num: int = 100):
    params = {
        "id": gallery_id,
        "page": page,
        "list_num": list_num,
    }
    res = requests.get(DC_LIST_URL, params=params, headers=HEADERS, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    posts = []
    rows = soup.select("table#gall_list tbody tr")

    for row in rows:
        if "notice" in row.get("class", []):
            continue

        title_tag = row.select_one("td.gall_tit a")
        writer_tag = row.select_one("td.gall_writer")
        date_tag = row.select_one("td.gall_date")
        count_tag = row.select_one("td.gall_count")
        recommend_tag = row.select_one("td.gall_recommend")

        if not title_tag or not title_tag.get("href"):
            continue

        href = title_tag["href"]
        if "no=" not in href:
            continue

        post_no = href.split("no=")[1].split("&")[0]

        posts.append({
            "no": post_no,
            "title": title_tag.get_text(strip=True),
            "link": "https://gall.dcinside.com" + href,
            "writer": writer_tag.get_text(strip=True) if writer_tag else "",
            "date": (date_tag.get("title") or date_tag.get_text(strip=True)) if date_tag else "",
            "views": count_tag.get_text(strip=True) if count_tag else "",
            "recommend": recommend_tag.get_text(strip=True) if recommend_tag else "",
        })

    return posts


def get_dc_post_detail(gallery_id: str, post_no: str):
    params = {"id": gallery_id, "no": post_no}
    res = requests.get(DC_VIEW_URL, params=params, headers=HEADERS, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    content_tag = soup.select_one("div.write_div")
    content = content_tag.get_text("\n", strip=True) if content_tag else ""

    return content


def crawl_dcbest(limit: int = 50, gallery_id: str = "dcbest"):
    """디시베스트(인기글) 크롤링 후 Firestore 저장"""
    saved_count = 0
    page = 1

    while saved_count < limit:
        posts = get_dc_list_page(gallery_id, page)
        if not posts:
            break

        for p in posts:
            if saved_count >= limit:
                break

            doc_id = f"dcinside_{gallery_id}_{p['no']}"
            doc_ref = db.collection("community_posts").document(doc_id)

            # 이미 저장된 글이면 스킵 (중복 방지)
            if doc_ref.get().exists:
                continue

            try:
                content = get_dc_post_detail(gallery_id, p["no"])
            except Exception as e:
                content = f"[본문 수집 실패: {e}]"

            doc_ref.set({
                "community": "dcinside",
                "board": gallery_id,
                "title": p["title"],
                "content": content,
                "writer": p["writer"],
                "date": p["date"],
                "views": p["views"],
                "recommend": p["recommend"],
                "url": p["link"],
                "crawled_at": firestore.SERVER_TIMESTAMP,
            })

            saved_count += 1
            time.sleep(random.uniform(0.5, 1.2))

        page += 1
        time.sleep(random.uniform(1.0, 2.0))

    return saved_count


# ─────────────────────────────
# MCP 도구 정의
# ─────────────────────────────
@mcp.tool()
def save_test():
    try:
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
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@mcp.tool()
def crawl_community(community: str, limit: int = 50):
    """
    지정된 커뮤니티의 인기글을 수집하여 Firestore에 저장한다.
    현재 지원: community="dcinside" (디시베스트 인기글)
    """
    if community != "dcinside":
        return {
            "community": community,
            "status": "error",
            "message": "현재는 'dcinside'만 지원합니다."
        }

    try:
        saved_count = crawl_dcbest(limit=limit)
        return {
            "community": community,
            "posts_collected": saved_count,
            "saved_to_firestore": True,
            "status": "success"
        }
    except Exception as e:
        return {
            "community": community,
            "status": "error",
            "message": str(e)
        }


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )