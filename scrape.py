import json
import time
import sqlite3

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://github.com/orgs/google/repositories"
HEADERS = {"User-Agent": "Mozilla/5.0 (class assignment)"}


def fetch_route(page, max_retry=5):
    """指定ページを取得して、リポジトリ一覧を含むデータを返す。429なら待ってやり直す"""
    for attempt in range(max_retry):
        res = requests.get(BASE_URL, params={"page": page}, headers=HEADERS)
        if res.status_code == 429:
            retry_after = res.headers.get("Retry-After", "")
            wait = int(retry_after) if retry_after.isdigit() else 60
            print(f"429 です。{wait}秒待ってやり直します ({attempt + 1}/{max_retry})")
            time.sleep(wait)
            continue
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        tag = soup.find("script", {"data-target": "react-app.embeddedData"})
        data = json.loads(tag.string)
        return data["payload"]["orgReposPageRoute"]
    raise RuntimeError(f"{page}ページ目の取得に失敗しました")


def extract(repos):
    rows = []
    for repo in repos:
        lang = repo["primaryLanguage"]["name"] if repo["primaryLanguage"] else None
        rows.append((repo["name"], lang, repo["starsCount"]))
    return rows

def save_to_db(rows, db_path="repos.db"):

    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS repositories (
            name     TEXT PRIMARY KEY,
            language TEXT,
            stars    INTEGER
        )
        """
    )
    conn.executemany(
        "INSERT OR REPLACE INTO repositories (name, language, stars) VALUES (?, ?, ?)",
        rows,
    )
    conn.commit()
    conn.close()


def show_db(db_path="repos.db"):
    conn = sqlite3.connect(db_path)
    print("件数:", conn.execute("SELECT COUNT(*) FROM repositories").fetchone()[0])
    for row in conn.execute(
        "SELECT name, language, stars FROM repositories ORDER BY stars DESC LIMIT 10"
    ):
        print(row)
    conn.close()

if __name__ == "__main__":
    START_PAGE = 1    # 途中で止まったら、止まったページ番号に変える
    MAX_PAGES = None  # テストするときは数字にする

    route = fetch_route(START_PAGE)
    page_count = route["pageCount"]
    last_page = page_count if MAX_PAGES is None else min(MAX_PAGES, page_count)

    for page in range(START_PAGE, last_page + 1):
        if page > START_PAGE:
            route = fetch_route(page)
        save_to_db(extract(route["repositories"]))
        print(f"{page}/{last_page} ページ完了")
        time.sleep(1)

    show_db()