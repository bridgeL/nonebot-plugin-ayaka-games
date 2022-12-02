import re
import requests
from bs4 import BeautifulSoup
from typing import List, Tuple
from ayaka import MessageSegment, Message

info_matcher = re.compile(r"(?P<desc>.*?)"
                          r"(?=视频播放量)(?P<digital>.*?)"
                          r"(?=视频作者)(?P<author>.*?)"
                          r"(?=相关视频)(?P<relate>.*)")
pic_matcher = re.compile(r"//(.*(jpg|png))$")
pic_tail_matcher = re.compile(r"@.*$")
title_tail_matcher = re.compile(r"_.*$")


async def deal(url: str):
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    head: BeautifulSoup = soup.head
    metas: List[BeautifulSoup] = head.find_all("meta")

    # 规定顺序
    params = {}

    data: List[Tuple[str, str]] = []
    for meta in metas:
        try:
            itemprop = meta["itemprop"]
            content = meta["content"]
            data.append((itemprop, content))
        except:
            continue

    for itemprop, content in data:
        r = pic_matcher.search(content)
        if r:
            content = "https://" + pic_tail_matcher.sub("", r.group(1))
            params["image"] = MessageSegment.image(content)

        elif itemprop == "description":
            r = info_matcher.search(content)
            if r:
                detail_dict = r.groupdict()
                for k, v in detail_dict.items():
                    params[k] = v
            else:
                params[itemprop] = content
        else:
            params[itemprop] = content

    url = params["url"]
    bv = url.rstrip("?/").rsplit("/", maxsplit=1)[-1]

    info = f'''
作者 - {params["author"]}
标题 - {title_tail_matcher.sub("", params["name"])}
地址 - {url}'''
    return Message([params["image"], info]), bv
