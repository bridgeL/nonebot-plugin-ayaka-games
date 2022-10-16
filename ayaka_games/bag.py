from ayaka import AyakaApp, MessageSegment

app = AyakaApp("bag")
app.help = '''背包（只是个存钱罐）
- 背包/bag
'''


async def show_money(uid: int, uname: str):
    money = inquire_money(uid)
    await app.send(f"[{uname}] 当前持有 {money}金")


@app.on_command(["背包", "bag"], super=True)
async def _():
    if not app.args:
        await show_money(app.user_id, app.user_name)
        return

    user = await get_user(app.args[0])

    if not user:
        await app.send("查无此人")
        return
    await show_money(user["user_id"], user["card"] or user["nickname"])


async def get_user(name_or_uid_or_at):
    '''通过name、at、uid中的任意一项获取user，若uid不在群内，返回None'''
    users = await app.bot.get_group_member_list(group_id=app.group_id)

    if isinstance(name_or_uid_or_at, MessageSegment) and name_or_uid_or_at.type == "at":
        at = name_or_uid_or_at
        try:
            uid = int(at.data["qq"])
        except:
            return

        for user in users:
            if user["user_id"] == uid:
                return user
        return

    # 名称？
    name = name_or_uid_or_at = str(name_or_uid_or_at)
    if name.startswith("@"):
        name = name[1:]

    # 群名片？
    for user in users:
        if user["card"] == name:
            return user

    # QQ昵称？
    for user in users:
        if user["nickname"] == name:
            return user

    # QQ号？
    try:
        uid = int(name_or_uid_or_at)
    except:
        return

    for user in users:
        if user["user_id"] == uid:
            return user


def inquire_money(uid: int):
    bag_file = app.group_storage(uid, default={})
    bag_data = bag_file.load()
    if "money" not in bag_data:
        bag_data["money"] = 1000
        bag_file.save(bag_data)
    return bag_data["money"]


def change_money(diff: int, uid: int):
    if diff == 0:
        return

    bag_file = app.group_storage(uid, default={})
    bag_data = bag_file.load()
    if "money" not in bag_data:
        bag_data["money"] = 1000

    bag_data["money"] += diff
    bag_file.save(bag_data)
    return bag_data["money"]
