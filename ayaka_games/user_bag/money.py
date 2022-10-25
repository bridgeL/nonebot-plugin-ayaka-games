from .app import app, User
from .utils import get_user


def get_money(uid: int):
    user = User(uid)
    return user.get("money", 1000)


def change_money(uid: int, diff: int):
    if diff == 0:
        return
    user = User(uid)
    money = user.get("money", 1000)
    money += diff
    user.set("money", money)
    return money


@app.on_command(["money", "财富", "金钱", "金币"], super=True)
async def _():
    if not app.args:
        money = get_money(app.user_id)
        await app.send(f"[{app.user_name}] 当前持有 {money}金")
        return

    user = await get_user(app.args[0])

    if not user:
        await app.send("查无此人")
        return

    uid = user["user_id"],
    uname = user["card"] or user["nickname"]
    money = get_money(uid)
    await app.send(f"[{uname}] 当前持有 {money}金")
