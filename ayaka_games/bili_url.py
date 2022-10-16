'''
    自动解析b站视频地址或小程序卡片
'''
from html import unescape
import json
import re
from typing import List, Tuple
from bs4 import BeautifulSoup
import requests
from ayaka import *

app = AyakaApp("bili_url")
app.help = "自动解析b站视频地址或小程序卡片"


url_matcher = re.compile(
    r"https://(b23\.tv|www\.bilibili\.com/video)(.*?\?|.*)")
info_matcher = re.compile(r"(?P<desc>.*?)"
                          r"(?=视频播放量)(?P<digital>.*?)"
                          r"(?=视频作者)(?P<author>.*?)"
                          r"(?=相关视频)(?P<relate>.*)")

pic_matcher = re.compile(r"(jpg|png)$")


@app.on_text(super=True)
async def auto_detect_bili_url():
    for m in app.message:
        if m.type == "json":
            data = str(json.loads(m.data['data']))
            break
    else:
        data = unescape(str(app.message))

    r = url_matcher.search(data)

    if r:
        url = r.group()
        await deal(url)


async def deal(url: str):
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    head: BeautifulSoup = soup.head
    metas: List[BeautifulSoup] = head.find_all("meta")

    # 规定顺序
    params = {
        "url": "",
        "image": "",
        "name": "",
        "author": "",
        "desc": ""
    }

    data: List[Tuple[str, str]] = []
    for meta in metas:
        try:
            itemprop = meta["itemprop"]
            content = meta["content"]
            data.append((itemprop, content))
        except:
            continue

    for itemprop, content in data:
        if pic_matcher.search(content):
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

    if not url:
        return

    await app.send(Message([
        params["image"],
        "作者 - ",
        params["author"],
        "\n标题 - ",
        params["name"].replace("_哔哩哔哩_bilibili", ""),
        f"\n地址 - {url}",
    ]))

    await app.send(bv)
