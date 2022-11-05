from ayaka import AyakaApp
from .utils import GroupUserFinder

app = AyakaApp("背包")
app.help = '''查看拥有财富'''


def get_user_prop(prop_name, uid, default):
    user_file = app.storage.group_path().json(uid)
    user_ctrl = user_file.chain(prop_name)
    return user_ctrl.get(default)


def set_user_prop(prop_name, uid, data):
    user_file = app.storage.group_path().json(uid)
    user_ctrl = user_file.chain(prop_name)
    user_ctrl.set(data)
    return data


def get_money(uid) -> int:
    return get_user_prop("金币", uid, 100)


def set_money(uid, money) -> int:
    return set_user_prop("金币", uid, money)


def change_money(uid, diff):
    return set_money(uid, get_money(uid) + diff)


def build_info(name, data: dict):
    if not data:
        return f"[{name}] 当前一无所有"
    items = [f"{k}: {v}" for k, v in data.items()]
    return f"[{name}]的背包\n" + "\n".join(items)


@app.on.idle(True)
@app.on.command("bag", "背包")
async def show_bag():
    user_path = app.storage.group_path()

    if not app.args:
        user_file = user_path.json(app.user_id)
        data = user_file.load()
        await app.send(build_info(app.user_name, data))
        return

    group_user_finder = GroupUserFinder(app.bot, app.group_id)
    user = await group_user_finder.get_user_by_segment(app.args[0])
    if not user:
        await app.send("查无此人")
        return

    uid = user["user_id"]
    name = user["card"] or user["nickname"]
    user_file = user_path.json(uid)
    data = user_file.load()
    await app.send(build_info(name, data))
