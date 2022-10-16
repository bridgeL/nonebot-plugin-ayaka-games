import re
from random import randint
from pypinyin import lazy_pinyin

from ayaka import *
from .bag import change_money, get_user


app = AyakaApp("成语接龙")
app.help = '''有效提高群文学氛围
游玩方法：聊天时发送成语即可
特殊命令一览：
- cy <成语>
- 什么是 <成语>
- <成语> 是什么
- 成语接龙统计 
'''


easy_chengyu_list: list = app.plugin_storage("easy", default={}).load()
py_list: list = app.plugin_storage("py", default={}).load()

search_bin: dict = app.plugin_storage("search", default={}).load()
whole_bin: dict = app.plugin_storage("meaning", default={}).load()
chengyu_list = list(whole_bin.keys())

q1_patt = re.compile(
    r'(啥|什么)是\s?(?P<data>[\u4e00-\u9fff]{3,}(.*[\u4e00-\u9fff]{3,})?)')
q2_patt = re.compile(
    r"(?P<data>[\u4e00-\u9fff]{3,}(.*[\u4e00-\u9fff]{3,})?)\s?是(啥|什么)(意思)?")
q3_patt = re.compile(
    r"(?P<data>[\u4e00-\u9fff]{3,}(.*[\u4e00-\u9fff]{3,})?)\s?是成语吗")
cy_patt = re.compile(r'[\u4e00-\u9fff]{3,}(.*[\u4e00-\u9fff]{3,})?')
not_zh_patt = re.compile(r"[^\u4e00-\u9fff]")


def check(msg):
    r = q1_patt.search(msg)
    if r:
        return False, r.group('data')

    r = q2_patt.search(msg)
    if r:
        return False, r.group('data')

    r = q3_patt.search(msg)
    if r:
        return True, r.group('data')


@app.on_text()
async def handle():
    msg = str(app.message)

    # 判断是不是在问问题
    item = check(msg)
    if item:
        f, msg = item
        await inquire(msg, must=f)
        return

    # 判断是否需要成语接龙
    # 3字以上的中文，允许包含一个间隔符，例如空格、顿号、逗号、短横线等
    r = cy_patt.search(msg)
    if not r:
        return

    # 删除标点
    msg = r.group()
    msg = not_zh_patt.sub("", msg)

    # 判断是否是成语
    if msg not in chengyu_list:
        return

    # 读取上次
    last = app.cache.last

    # 判断是否成功
    py1 = lazy_pinyin(msg[0])[0]
    if py1 == last:
        change_money(1000, app.user_id)
        await app.send(f"[{app.user_name}] 奖励1000金")
        file = app.group_storage(app.user_id, default={})
        data: dict = file.load()
        data["cnt"] = data.get("cnt", 0) + 1
        file.save(data)

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
        change_money(10000, app.user_id)
        app.cache.last = ""
        await app.send(f"[{app.user_name}] 奖励10000金")


# 用户询问
async def inquire(msg: str, must=False):
    # 删除标点
    msg = not_zh_patt.sub("", msg)
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
                await app.send_many(app.group_id, rs[:10])


@app.on_command("成语接龙统计")
async def handle():
    if app.args:
        user = await get_user(app.args[0])
        if not user:
            await app.send("查无此人")
            return
        uid = user["user_id"]
        name = user["card"] or user["nickname"]
    else:
        uid = app.user_id
        name = app.user_name

    file = app.group_storage(uid, default={})
    data: dict = file.load()
    cnt = data.get("cnt", 0)

    await app.send(f"[{name}] 从本功能诞生起至今已成功接龙 {cnt}次~")
