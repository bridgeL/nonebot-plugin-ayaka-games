'''
    自动解析b站视频地址或小程序卡片
'''
import re
import requests
from bs4 import BeautifulSoup
from typing import List, Tuple
from ayaka import AyakaApp, MessageSegment, Message

app = AyakaApp("b站视频地址解析")
app.help = "自动解析b站视频地址"


url_matcher = re.compile(
    r"https://(b23\.tv|(www|m)\.bilibili\.com/video)(.*?\?|.*)")
info_matcher = re.compile(r"(?P<desc>.*?)"
                          r"(?=视频播放量)(?P<digital>.*?)"
                          r"(?=视频作者)(?P<author>.*?)"
                          r"(?=相关视频)(?P<relate>.*)")
pic_matcher = re.compile(r"(jpg|png)$")


@app.on.idle(True)
@app.on.text()
async def detect_url():
    data = app.event.get_plaintext()
    r = url_matcher.search(data)
    if r:
        url = r.group()
        msg, bv = await deal(url)
        if bv:
            await app.send(msg)
            await app.send(bv)


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

    info = f'''
作者 - {params["author"]}
标题 - {params["name"].replace("_哔哩哔哩_bilibili", "")}
地址 - {url}'''

    return Message([params["image"], info]), bv
