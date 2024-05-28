import requests
import os

PLEX_TOKEN = "LKxyrJqXa59BxSyVox7C"
PLEX_URL = "https://4887.pirately.cc"
RSS_URL = "https://rss.plex.tv/ca89d3c6-543c-4a4d-a62e-4dcb45aed6c6"
REQUEST_URL = "https://overseerr.blackbeard.shop/api/v1/request"

# os.environ['HTTPS_PROXY'] = 'http://10.0.10.96:9090'
# os.environ['HTTP_PROXY'] = 'http://10.0.10.96:9090'
# r = requests.post('http://wikipedia.org', cookies=cookies)

def request_rss(url):
    r = requests.get(
        url, headers={"content-type": "application/json", "accept": "application/json"}
    )
    return  r.json()

def run():
    data = request_rss(RSS_URL)
    process_items(data["items"])
    if data["links"]["next"]:
        data = request_rss(data["links"]["next"])
        process_items(data["items"])   

def process_items(items):

    for item in items:
        if not item["guids"]:
            continue

        tmdb = None
        tvdb = None
        for guid in item["guids"]:
            if guid.startswith("tmdb"):
                tmdb = int(guid.strip("tmdb://"))

            if guid.startswith("tvdb"):
                tvdb = int(guid.strip("tvdb://"))
                break

        if not tmdb:
            continue

        # {"mediaId":65055,"tvdbId":272899,"mediaType":"tv","is4k":false,"seasons":[1]}

        mediaType = item["category"]
        if mediaType == "show":
            mediaType = "tv"

        data = {"mediaId": int(tmdb), "mediaType": mediaType, "is4k": False}
        if mediaType == "tv":
            data["tvdbId"] = tvdb
            data["seasons"] = "all"

        # data = {"mediaId":65055,"tvdbId":272899,"mediaType":"tv","is4k":False,"seasons":"all"}
        r = requests.post(
            REQUEST_URL,
            headers={
                "content-type": "application/json",
                "accept": "application/json",
                "Cookie": "connect.sid=s%3ARw1BBWGv0Dswd2qzKOQOTZQu4YFWghEn.QgqxQeyCHbE44IqbJYKBM9uQ3z0ALgvzuDCBn6OqKhI",
            },
            json=data,
        )
        print(r.json())
        #break
