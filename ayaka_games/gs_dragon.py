import re
from random import randint
from pypinyin import lazy_pinyin
from ayaka import *

app = AyakaApp("原神接龙")
app.help = "原神接龙，关键词中了就行"

not_zh = re.compile(r'[^\u4e00-\u9fa5]*')

# 语料库
words = app.plugin_storage("bin", default={}).load()
search_bin = app.plugin_storage("search", default={}).load()


@app.on_text()
async def handle():
    msg = str(app.message)

    # 删除所有非汉字
    msg = not_zh.sub('', msg)

    if not msg:
        return

    if msg not in words:
        return

    py = lazy_pinyin(msg[-1])[0]
    if py not in search_bin:
        return

    ans_list = search_bin[py]
    if ans_list:
        ans = ans_list[randint(0, len(ans_list)-1)]
        await app.send(ans)
