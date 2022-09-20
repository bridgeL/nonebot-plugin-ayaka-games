import re
from random import randint
from pypinyin import lazy_pinyin

from ayaka import *
from ..bag import add_money
from ..utils.name import get_name, get_uid_name
from ..utils.file import LocalPath

app = AyakaApp("成语接龙", only_group=True)
app.help = "成语接龙（肯定是你输\n[#cy <参数>] 查询成语\n[什么是 <参数>] 查询成语\n[<参数> 是什么] 查询成语\n[#成语统计] 查询历史记录"

path = LocalPath(__file__)
search_bin: dict = path.load_json("search")
whole_bin: dict = path.load_json("meaning")
chengyu_list = list(whole_bin.keys())


def check(msg):
    r = re.search(
        r'(啥|什么)是\s?(?P<data>[\u4e00-\u9fff]{3,}(.*[\u4e00-\u9fff]{3,})?)', msg)
    if r:
        return r.group('data'), False

    r = re.search(
        r"(?P<data>[\u4e00-\u9fff]{3,}(.*[\u4e00-\u9fff]{3,})?)\s?是(啥|什么)(意思)?", msg)
    if r:
        return r.group('data'), False

    r = re.search(
        r"(?P<data>[\u4e00-\u9fff]{3,}(.*[\u4e00-\u9fff]{3,})?)\s?是成语吗", msg)
    if r:
        return r.group('data'), True


@app.on_text()
async def handle():
    msg = str(app.message)
    name = get_name(app.event)

    # 判断是不是在问问题
    item = check(msg)
    if item:
        msg, must = item
        await inquire(msg, must)
        return

    # 判断是否需要成语接龙
    # 3字以上的中文，允许包含一个间隔符，例如空格、顿号、逗号、短横线等
    r = re.search(r'[\u4e00-\u9fff]{3,}(.*[\u4e00-\u9fff]{3,})?', msg)
    if not r:
        return

    # 删除标点
    msg = r.group()
    msg = re.sub(r"[^\u4e00-\u9fff]", "", msg)

    # 判断是否是成语
    if msg not in chengyu_list:
        return

    # 读取上次
    last = app.cache.last

    # 判断是否成功
    py1 = lazy_pinyin(msg[0])[0]
    if py1 == last:
        add_money(1000, app.device, app.event.user_id)
        await app.send(f"[{name}] 奖励1000金")
        sa = app.storage.accessor(app.event.user_id)
        sa.inc()

    # 准备下次
    ans = None
    py = lazy_pinyin(msg[-1])[0]
    if py in search_bin:
        vs = search_bin[py]

        # 适当放水，可选择回答越少的放水越多
        i = randint(0, len(vs)+1)
        if i < len(vs):
            ans = vs[i]

    # 是否有回应
    if ans:
        py2 = lazy_pinyin(ans[-1])[0]
        ans = f"[{py}] {ans} [{py2}]"
        await app.send(ans)

        # 保存
        app.cache.last = py2

    else:
        await app.send("你赢了")

        add_money(10000, app.device, app.event.user_id)
        app.cache.last = ""
        await app.send(f"[{name}] 奖励10000金")


# 用户询问
async def inquire(msg: str, must=False):
    # 删除标点
    msg = re.sub(r"[^\u4e00-\u9fff]", "", msg)
    # 判断是否是成语
    if msg not in chengyu_list:
        if not must:
            return
        await app.send(f"[{msg}] 不是成语")
    else:
        pys = lazy_pinyin(msg)
        ans = " ".join(pys)

        val = whole_bin[msg]
        ans = f"[{msg}]\n[{ans}]\n\n{val}"
        await app.send(ans)


@app.on_command(["cy", "成语"])
async def handle():
    arg = str(app.message).strip()
    if not app.args:
        await app.send(app.help)
    else:
        if not await inquire(app.args[0], must=True):
            rs = []
            for key in whole_bin:
                val = whole_bin[key]
                if arg in val or arg in key:
                    rs.append(key + "\n" + val)
            if rs:
                await app.bot.send_group_forward_msg(app.event.group_id, rs[:10])


@app.on_command("成语统计")
async def handle():
    if app.args:
        uid, name = await get_uid_name(app.bot, app.event, app.args[0])
    else:
        uid = app.event.user_id
        name = get_name(app.event)

    if not uid:
        await app.send("查无此人")
        return

    sa = app.storage.accessor(uid)
    cnt = sa.get(0)

    await app.send(f"[{name}] 从本功能诞生起至今已成功接龙 {cnt}次~")
