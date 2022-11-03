'''
    自动解析b站小程序卡片
'''
import re
import json
from ayaka import AyakaApp
from .url import deal

app = AyakaApp("b站小程序卡片解析")
app.help = "自动解析b站小程序卡片"


url_matcher = re.compile(
    r"https://(b23\.tv|www\.bilibili\.com/video)(.*?\?|.*)")


def get_all_values(data: dict):
    values = []
    for value in data.values():
        if isinstance(value, dict):
            values.extend(get_all_values(value))
        else:
            values.append(value)
    return values


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
            r = url_matcher.search(v)
            if r:
                url = r.group()
                msg, bv = await deal(url)
                if bv:
                    await app.send(msg)
                    await app.send(bv)
