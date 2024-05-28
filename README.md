Push your plex watchlist to overseerr.

### Install
`pip install -r requirement.txt`

### run script
`EMAIL="myemail" PASSWORD="mypassword" WATCHLIST_URL="watchlisturl" python src/main.py`

Multiple watchlists are supported by using `,` as seperator: `WATCHLIST_URL="watchlisturl,myfriendswatchlist"`

Watchlist urls can be found here: https://app.plex.tv/desktop/#!/settings/watchlist

There is also an docker image avaiable at: `ghcr.io/lostb1t/ghcr.io/lostb1t/overseerrwatchlist:latest`