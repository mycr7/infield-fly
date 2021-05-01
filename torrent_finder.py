"""Module for retrieving torrent file data"""

import platform
from datetime import datetime, timedelta
from time import sleep
import requests


class TorrentDataProvider:

    """Provider to retrieve torrent data from rarbg.to"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://torrentapi.org/pubapi_v2.php"
        self.token = None
        self.token_expiration = None
        self.last_request = None

    @property
    def user_agent(self):
        """Gets the user agent string to be used with the torrent API"""

        return "{}/{} ({}) python {}".format(
            "infield-fly",
            "1.0",
            "; ".join(platform.uname()),
            platform.python_version())

    def get_token(self):
        """Gets the API token for use with the torrent API"""

        params = { "get_token": "get_token", "app_id": "infield-fly" }
        token_response = self.get_data(params)
        print("Geting API token")
        if "error" in token_response:
            print("Error retrieving token")
        else:
            self.token = token_response["token"]
            self.token_expiration = datetime.now() + timedelta(minutes=10)
            print("Token retrieved: {}".format(self.token))

    def get_data(self, params = None):
        """Gets data from the torrent API, waiting between calls if necessary"""

        if self.last_request is not None:
            seconds_since_last_request = (datetime.now() - self.last_request).total_seconds()
            if seconds_since_last_request < 2.0:
                print("Too soon for API. Waiting...")
                sleep(2.0 - seconds_since_last_request)

        headers = { "User-Agent": self.user_agent, "Accept": "application/json" }
        response = requests.get(self.base_url, params = params, headers = headers)
        self.last_request = datetime.now()

        if response.status_code != 200:
            return None

        return response.json()

    def search(self, search_string, retry_count=4):
        """
        Searches for a string using the torrent API, retrying up to the specified
        number of times
        """

        if self.token is None:
            self.get_token()

        params = {
            "mode": "search",
            "search_string": search_string,
            "token": self.token,
            "format": "json_extended",
            "app_id": "infield-fly"
        }

        print("Searching for '{}'".format(search_string))
        search_response = self.get_data(params)
        while "error" in search_response and retry_count > 0:
            print("No results received; waiting and trying again...")
            sleep(3)
            retry_count -= 1
            search_response = self.get_data(params)

        if "error" in search_response:
            return []

        torrent_results = []
        for torrent_result in search_response["torrent_results"]:
            torrent_results.append(TorrentResult.from_dictionary(torrent_result))

        return torrent_results


class TorrentResult:

    """Describes a torrent search result"""

    def __init__(self, title, magnet_link, tvdb_id):
        super().__init__()
        self.title = title
        self.magnet_link = magnet_link
        self.tvdb_id = tvdb_id

    @classmethod
    def from_dictionary(cls, torrent_dict):
        """Creates a TorrentResult from a dictionary, usually from a JSON object"""

        title = torrent_dict["title"]
        magnet_link = torrent_dict["download"]
        tvdb_id = None
        if "episode_info" in torrent_dict and "tvdb" in torrent_dict["episode_info"]:
            tvdb_id = int(torrent_dict["episode_info"]["tvdb"])

        return TorrentResult(title, magnet_link, tvdb_id)
