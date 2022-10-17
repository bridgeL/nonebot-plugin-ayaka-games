import requests
import datetime
from typing import List
from ayaka import AyakaApp, get_new_page, logger, MessageSegment
from pydantic import BaseModel

app = AyakaApp("bili_dy")
app.help = """24h视奸b站up动态
- bili_dy_add <id> 添加
- bili_dy_del <id> 删除
"""

mid_file = app.plugin_storage("mids", default=[])
uid_file = app.plugin_storage("uids", default=[])

code = '''
document.querySelector("#internationalHeader").style = 'display:none';
document.querySelector("body>.van-popover.van-popper").style = 'display:none';
'''


class _Group(BaseModel):
    group_id: int
    bot_id: int


class _Up(BaseModel):
    uid: int
    name: str
    groups: List[_Group] = []

    def find(self, bot_id: int, group_id: int):
        for g in self.groups:
            if g.bot_id == bot_id and g.group_id == group_id:
                return g


class _UpList(BaseModel):
    value: List[_Up] = []

    def find(self, uid: int):
        for up in self.value:
            if up.uid == uid:
                return up


def load():
    return _UpList(value=uid_file.load())


def save(up_list: _UpList):
    uid_file.save(up_list.dict()["value"])


async def get_screenshot(link: str, name: str):
    path = app                                  \
        .plugin_storage("pics", suffix=None)    \
        .path.joinpath(f"{name}.png")           \
        .absolute()

    async with get_new_page(device_scale_factor=2) as page:
        await page.goto(link, wait_until="networkidle")
        await page.wait_for_selector(".bili-dyn-item__main")
        await page.evaluate(code)
        await page.locator(".bili-dyn-item__main").screenshot(path=path)
    return path


def get(uid):
    url = f"https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={uid}"
    data = requests.get(url).json()
    return data


def get_links(uid):
    data = get(uid)

    try:
        cards = data["data"]["cards"]
    except:
        return

    date = datetime.datetime.now().date()
    mids: list = mid_file.load()

    links: List[str] = []

    for card in cards:
        mid = card['desc']['dynamic_id']
        link = f"https://t.bilibili.com/{mid}"
        _date = datetime.datetime.fromtimestamp(
            card['desc']['timestamp']).date()
        if _date == date and mid not in mids:
            mids.append(mid)
            links.append(link)

    if links:
        mid_file.save(mids)

    return links


@app.on_interval(60)
async def handle():
    up_list = load()
    for up in up_list.value:
        # 查看动态
        links = get_links(up.uid)

        # 依次截图、下载、发送
        for link in links:
            name = link.split("/")[-1]
            logger.success(f"正在截图 {link}")
            image_path = await get_screenshot(link, name)
            image = MessageSegment.image(image_path)

            # 依次发送
            for g in up.groups:
                await app.t_send(bot_id=g.bot_id, group_id=g.group_id, message=link)
                await app.t_send(bot_id=g.bot_id, group_id=g.group_id, message=image)


@app.on_command("bili_dy_add")
async def add():
    if not app.args:
        await app.send("参数缺失")
        return

    try:
        uid = int(str(app.args[0]))
    except:
        await app.send("参数错误")
        return

    up_list = load()
    up = up_list.find(uid)
    if up:
        g = up.find(app.bot_id, app.group_id)
        if g:
            await app.send(f"{up.name}({uid}) 已经添加过")
            return
    else:
        try:
            card = get(uid)["data"]["cards"][0]
            name = card["desc"]["user_profile"]["info"]["uname"]
            up = _Up(uid=uid, name=name)
            up_list.value.append(up)
        except:
            await app.send(f"{uid} 不存在")
            return

    up.groups.append(_Group(group_id=app.group_id, bot_id=app.bot_id))
    save(up_list)
    await app.send(f"{up.name}({uid}) 添加成功")


@app.on_command("bili_dy_del")
async def add():
    if not app.args:
        await app.send("参数缺失")
        return

    try:
        uid = int(str(app.args[0]))
    except:
        await app.send("参数错误")
        return

    up_list = load()
    up = up_list.find(uid)
    if not up:
        await app.send(f"{uid} 不在追踪列表中")
        return

    g = up.find(app.bot_id, app.group_id)
    if not g:
        await app.send(f"{up.name}({uid}) 不在追踪列表中")
        return

    up.groups.remove(g)
    save(up_list)
    await app.send(f"{up.name}({uid}) 移除成功")
