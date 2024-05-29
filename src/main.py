import sys
import requests
from requests.adapters import HTTPAdapter, Retry
import os

REQUEST_URL = "https://overseerr.blackbeard.shop/api/v1/request"

email = os.environ["EMAIL"]
password = os.environ["PASSWORD"]
watchlist_urls = os.environ["WATCHLIST_URL"].split(",")

retry_strategy = Retry(
    total=4,
    status_forcelist=[429, 500, 502, 503, 504],
)

adapter = HTTPAdapter(max_retries=retry_strategy)

class WatchlistRunner:
    session = None
    movie_quota_reached = False
    tv_quota_reached = False

    def login(self):
        r = self.session.post(
            "https://overseerr.blackbeard.shop/api/v1/auth/local", 
            headers={"content-type": "application/json", "accept": "application/json"}, 
            json={"email": email, "password": password}
        )
        return r

    def get_watchlist(self, url):
        r = self.session.get(
            url, headers={"content-type": "application/json", "accept": "application/json"}
        )
        return  r.json()

    def get_media(self, id, media_type):
        url = "https://overseerr.blackbeard.shop/api/v1/{}/{}".format(media_type, id)
        r = self.session.get(
            url, headers={"content-type": "application/json", "accept": "application/json"}
        )
        return  r.json()

    def run(self):
        self.session = requests.Session()
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        r = self.login()

        for uri in watchlist_urls:
            self.process(uri)

    def process(self, uri):
        print("--- Processing watchlist: {} ---".format(uri))
        data = self.get_watchlist(uri)
        self.process_items(data["items"])

        if 'next' in data["links"]:
            self.process(data["links"]["next"]) 

    def process_items(self, items):
        for item in items:
            if self.tv_quota_reached and self.movie_quota_reached:
                print("Quotas reached, ending run.")
                sys.exit(0)

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

            media_type = item["category"]
            if media_type == "show":
                media_type = "tv"
                

            print("{}: ".format(item['title']), end='')

            if media_type == "tv" and self.tv_quota_reached:
                print("Series quota reached, skipping.")
            if media_type == "movie" and self.movie_quota_reached:
                print("Movie quota reached, skipping.")
    
            media = self.get_media(tmdb, media_type)
            if "mediaInfo" in media and media["mediaInfo"]["status"] > 1:
                # already avaiable or requested
                # todo: handle partial avaiable
                print("Already avaiable/requested, skipping.")
                continue
                

            data = {"mediaId": int(tmdb), "mediaType": media_type, "is4k": False}
            if media_type == "tv":
                data["tvdbId"] = tvdb
                data["seasons"] = "all"

            print("requesting", end='')

            r = self.session.post(
                REQUEST_URL,
                headers={
                    "content-type": "application/json",
                    "accept": "application/json",
                },
                json=data,
            )
            #print(r.status_code)
            if r.ok:
                print(" - success")
            else:
                print(" - error: {}".format(r.text))
                if r.json()["message"].lower() == "series quota exceeded.":
                    self.tv_quota_reached = True
                if r.json()["message"].lower() == "movie quota exceeded.":
                    self.movie_quota_reached = True


if __name__ == "__main__":
    runner = WatchlistRunner()
    runner.run()
