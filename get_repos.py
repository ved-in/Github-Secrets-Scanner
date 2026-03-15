import os
import requests
import zipfile
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json"
}

if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"
    

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

for f in os.listdir(DOWNLOAD_DIR):
    path = os.path.join(DOWNLOAD_DIR, f)
    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        import shutil
        shutil.rmtree(path)


def is_valid_zip(path):
    try:
        with zipfile.ZipFile(path, 'r') as z:
            return len(z.namelist()) > 0
    except:
        return False


def download_repo(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/zipball"
    filename = f"{owner}_{repo}.zip"
    path = os.path.join(DOWNLOAD_DIR, filename)

    r = requests.get(url, headers=HEADERS)

    if r.status_code != 200:
        print(f"Failed: {owner}/{repo} ({r.status_code})")
        return

    if "application/zip" not in r.headers.get("content-type", ""):
        print(f"Not a zip. Skipping {owner}/{repo}")
        return

    with open(path, "wb") as f:
        f.write(r.content)

    if not is_valid_zip(path):
        print(f"Invalid zip. Deleting {filename}")
        os.remove(path)
        return

    print(f"Saved {filename}")


def get_recent_repos():
    search_url = "https://api.github.com/search/repositories"
    params = {
        "q": "is:public",
        "sort": "updated",
        "order": "desc",
        "per_page": 5 
    }

    r = requests.get(search_url, headers=HEADERS, params=params)

    if r.status_code != 200:
        print(f"Failed to fetch repos: {r.status_code}")
        return

    items = r.json().get("items", [])
    if not items:
        print("No repos found")
        return

    for repo in items:
        download_repo(repo["owner"]["login"], repo["name"])


if __name__ == "__main__":
    get_recent_repos()  