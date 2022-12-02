'''
    自动解析b站视频地址或小程序卡片
'''
import re
from .app import app
from .utils import deal


url_matcher = re.compile(
    r"https://(b23\.tv|(www|m)\.bilibili\.com/video)(.*?\?|.*)")


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
