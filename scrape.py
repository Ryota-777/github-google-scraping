import time
import requests

URL = "https://github.com/orgs/google/repositories"

res = requests.get(URL, headers={"User-Agent": "Mozilla/5.0 (class assignment)"})
print(res.status_code)

with open("page1.html", "w", encoding="utf-8") as f:
    f.write(res.text)

time.sleep(1)