import requests
import os

RSS_URL = "https://rss.plex.tv/c74d1ad2-ca5f-4f97-8a87-6da8ceb846f3"
RSS_URL_FRIENDS = "https://rss.plex.tv/ca89d3c6-543c-4a4d-a62e-4dcb45aed6c6"
REQUEST_URL = "https://overseerr.blackbeard.shop/api/v1/request"

def request_rss(url):
    r = requests.get(
        url, headers={"content-type": "application/json", "accept": "application/json"}
    )
    return  r.json()

def run():
    for uri in [RSS_URL, RSS_URL_FRIENDS]:
        data = request_rss(uri)
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

        mediaType = item["category"]
        if mediaType == "show":
            mediaType = "tv"

        data = {"mediaId": int(tmdb), "mediaType": mediaType, "is4k": False}
        if mediaType == "tv":
            data["tvdbId"] = tvdb
            data["seasons"] = "all"

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

if __name__ == "__main__":
    run()