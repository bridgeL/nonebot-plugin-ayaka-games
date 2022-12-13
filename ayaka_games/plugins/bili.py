'''
    自动解析b站视频地址或小程序卡片
'''
import re
import json
import requests
from bs4 import BeautifulSoup
from typing import List, Tuple
from ayaka import AyakaApp, MessageSegment, Message

app = AyakaApp("b站视频地址解析")
app.help = "自动解析b站视频地址"


card_url_matcher = re.compile(
    r"https://(b23\.tv|www\.bilibili\.com/video)(.*?\?|.*)")


def get_all_values(data: dict):
    values = []
    for value in data.values():
        if isinstance(value, dict):
            values.extend(get_all_values(value))
        else:
            values.append(value)
    return values


url_matcher = re.compile(
    r"https://(b23\.tv|(www|m)\.bilibili\.com/video)(.*?\?|.*)")


@app.on.idle(True)
@app.on.text()
async def detect_card():
    for m in app.message:
        if m.type == "json":
            data: dict = json.loads(m.data['data'])
            break
    else:
        return

    # 提取所有层级的values
    values = get_all_values(data)

    for v in values:
        if isinstance(v, str):
            # 从card中抓取网址
            r = card_url_matcher.search(v)
            if r:
                url = r.group()
                msg, bv = await deal(url)
                if bv:
                    await app.send(msg)
                    await app.send(bv)


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
