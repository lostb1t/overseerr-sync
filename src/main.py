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
    cookie = None
    session = None

    def login(self):
        r = requests.post(
            "https://overseerr.blackbeard.shop/api/v1/auth/local", 
            headers={"content-type": "application/json", "accept": "application/json"}, 
            json={"email": email, "password": password}
        )
        # print(r.cookies.get_dict())
        self.cookie = r.headers["set-cookie"]
        return r

    def get_watchlist(self, url):
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
        # print(data)
        self.process_items(data["items"])
        if 'next' in data["links"]:
            self.process(data["links"]["next"]) 

    def process_items(self, items):
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

            print("requesting: {} ".format(item['title']), end='')
            r = self.session.post(
                REQUEST_URL,
                headers={
                    "content-type": "application/json",
                    "accept": "application/json",
                    "Cookie": self.cookie,
                },
                json=data,
            )
            if r.ok:
                print("success")
            else:
                print("error: {}".format(r.text))


if __name__ == "__main__":
    runner = WatchlistRunner()
    runner.run()
