import requests
from bs4 import BeautifulSoup
from ayaka import logger
from .utils import combine_url, div_url, get_user_agent

class Spider:
    def __init__(self, url="", params={}, cookie="", headers={}, proxy="") -> None:
        self.api, self.params = div_url(url)
        self.params.update(params)
        self.cookie = cookie
        self.headers = headers
        self.proxy = {"http": proxy, "https": proxy} if proxy else ""

    @property
    def url(self):
        return combine_url(self.api, self.params)

    @url.setter
    def url(self, url: str):
        self.api, params = div_url(url)
        self.params.update(params)

    def get_res(self) -> requests.Response:
        logger.debug(f"正在爬取 {self.url}")

        config = {
            "url": self.api,
            "params": self.params,
            "headers": self.headers
        }

        config['headers']['user-agent'] = get_user_agent()

        if self.cookie:
            config['headers']['cookie'] = self.cookie

        if self.proxy:
            config["proxies"] = self.proxy

        return requests.get(**config)

    def get_json(self) -> dict:
        return self.get_res().json()

    def get_soup(self):
        data = self.get_res().content
        return BeautifulSoup(data, "html.parser")
