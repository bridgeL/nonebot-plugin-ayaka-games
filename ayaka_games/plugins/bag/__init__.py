from ayaka import AyakaApp
from .utils import GroupUserFinder

app = AyakaApp("背包")
app.help = '''查看拥有财富'''


def get_user(uid) -> dict:
    file = app.storage.group().jsonfile(uid)
    return file.load()


def get_user_prop(prop_name, uid, default):
    file = app.storage.group().jsonfile(uid).keys(prop_name)
    return file.get(default)


def set_user_prop(prop_name, uid, data):
    file = app.storage.group().jsonfile(uid).keys(prop_name)
    file.set(data)
    return data


def get_money(uid) -> int:
    return get_user_prop("金币", uid, 100)


def set_money(uid, money) -> int:
    return set_user_prop("金币", uid, money)


def change_money(uid, diff):
    return set_money(uid, get_money(uid) + diff)


@app.on.idle(True)
@app.on.command("bag", "背包")
async def show_bag():
    if not app.args:
        uid = app.user_id
        name = app.user_name
        data = get_user(uid)
        if not data:
            await app.send(f"[{name}] 当前一无所有")
        else:
            items = [f"{k}: {v}" for k, v in data.items()]
            await app.send(f"[{name}]的背包\n" + "\n".join(items))
        return

    group_user_finder = GroupUserFinder(app.bot, app.group_id)
    user = await group_user_finder.get_user_by_segment(app.args[0])
    if not user:
        await app.send("查无此人")
        return

    uid = user["user_id"]
    name = user["card"] or user["nickname"]
    data = get_user(uid)
    if not data:
        await app.send(f"[{name}] 当前一无所有")
    else:
        items = [f"{k}: {v}" for k, v in data.items()]
        await app.send(f"[{name}]的背包\n" + "\n".join(items))
