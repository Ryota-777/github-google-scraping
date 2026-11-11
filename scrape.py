import json
import time

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://github.com/orgs/google/repositories"
HEADERS = {"User-Agent": "Mozilla/5.0 (class assignment)"}


def fetch_route(page):
    """指定ページを取得して、リポジトリ一覧を含むデータを返す"""
    res = requests.get(BASE_URL, params={"page": page}, headers=HEADERS)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    tag = soup.find("script", {"data-target": "react-app.embeddedData"})
    data = json.loads(tag.string)
    return data["payload"]["orgReposPageRoute"]


def extract(repos):
    """リポジトリのリストから (名前, 言語, スター数) のリストを作る"""
    rows = []
    for repo in repos:
        lang = repo["primaryLanguage"]["name"] if repo["primaryLanguage"] else None
        rows.append((repo["name"], lang, repo["starsCount"]))
    return rows


if __name__ == "__main__":
    MAX_PAGES = 3  # まずは3ページでテスト。動いたら None にする

    all_repos = {}  # 名前 -> (名前, 言語, スター数)

    route = fetch_route(1)
    page_count = route["pageCount"]
    last_page = page_count if MAX_PAGES is None else min(MAX_PAGES, page_count)

    for page in range(1, last_page + 1):
        if page > 1:
            route = fetch_route(page)
        for row in extract(route["repositories"]):
            all_repos[row[0]] = row
        print(f"{page}/{last_page} ページ完了 (累計 {len(all_repos)} 件)")
        time.sleep(1)

    print("取得件数:", len(all_repos))