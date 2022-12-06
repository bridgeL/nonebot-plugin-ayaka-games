from pydantic import Field
from typing import Optional, Union
from ayaka import AyakaApp, AyakaInputModel, msg_type, MessageSegment

app = AyakaApp("背包")
app.help = '''查看拥有财富'''

msg_at = msg_type("at")


class UserInput(AyakaInputModel):
    value: Optional[Union[msg_at, int, str]] = Field(
        description="查询目标的QQ号/名称/@xx")

    def is_uid(self):
        return isinstance(self.value, (MessageSegment, int))

    def get_value(self):
        if isinstance(self.value, MessageSegment):
            return int(self.value.data["qq"])
        if isinstance(self.value, str) and self.value.startswith("@"):
            return self.value[1:]
        return self.value


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
@app.on_model(UserInput)
async def show_bag():
    user_path = app.storage.group_path()
    data: UserInput = app.model_data
    print(data.value)

    if not data.value:
        user_file = user_path.json(app.user_id)
        data = user_file.load()
        await app.send(build_info(app.user_name, data))
        return

    users = await app.bot.get_group_member_list(group_id=app.group_id)
    value = data.get_value()

    if data.is_uid():
        for user in users:
            uid = user["user_id"]
            if uid == value:
                name = user["card"] or user["nickname"]
                break
        else:
            uid = 0
    else:
        for user in users:
            name = user["card"] or user["nickname"]
            if name == value:
                uid = user["user_id"]
                break
        else:
            uid = 0

    if not uid:
        await app.send("查无此人")
        return

    user_file = user_path.json(uid)
    data = user_file.load()
    await app.send(build_info(name, data))
