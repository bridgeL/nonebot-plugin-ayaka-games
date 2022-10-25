from ayaka import MessageSegment
from .app import app


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
