from .money import get_money, change_money
from .app import User, app


def get_mana(uid: int):
    user = User(uid)
    return user.get("mana", 0)


def change_mana(uid: int, diff: int):
    user = User(uid)
    mana = user.get("mana", 0)
    mana += diff
    user.set("mana", mana)
    return mana


@app.on_command(['mana', '玛娜'])
async def handle():
    try:
        arg = int(str(app.args[0]))
    except:
        arg = 0

    name = app.user_name
    uid = app.user_id
    if arg != 0:
        money = get_money(uid)
        if money - arg*1000 < 0:
            await app.send(f"[{name}] 只有 [{money}]金")
            return

        mana = get_mana(uid)
        if mana + arg < 0:
            await app.send(f"[{name}] 只有 [{mana}]玛娜")
            return

        mana = change_mana(uid, arg)
        money = change_money(uid, -1000*arg)
        await app.send(f"[{name}] 花费了 {arg*1000}金，获得了 {arg}玛娜")

    else:
        money = get_money(uid)
        mana = get_mana(uid)

    await app.send(f"[{name}] 当前有 {money}金，{mana}玛娜")
