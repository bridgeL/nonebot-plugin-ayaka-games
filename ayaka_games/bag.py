'''
    背包
'''
from ayaka import *
from .utils.name import get_name, get_uid_name

app = AyakaApp('bag', only_group=True)
app.help = "背包"


@app.on_command(['bag', '背包'], super=True)
async def bag():
    # 如果附带参数，则查询指定人
    if len(app.args) >= 1:
        uid, name = await get_uid_name(app.bot, app.event, app.args[0])
        if not uid:
            await app.send("查无此人")
            return

    # 否则查询自己
    else:
        uid = app.event.user_id
        name = get_name(app.event)

    money = get_money(app.device, uid)

    ans = f"[{name}] 当前有 {money}金"
    await app.send(ans)


def get_money(device: AyakaDevice, uid: int) -> int:
    _app = device.get_app(app.name)
    sa = _app.storage.accessor(uid, "money")
    money = sa.get()
    if money is None:
        # 初始100金
        sa.set(100)
        return 100
    return money


def add_money(diff: int, device: AyakaDevice, uid: int) -> int:
    _app = device.get_app(app.name)
    sa = _app.storage.accessor(uid, "money")
    money = sa.get()
    if money is None:
        # 初始100金
        money = 100 + diff
        sa.set(money)
    else:
        money += diff
        sa.set(money)
    return money
