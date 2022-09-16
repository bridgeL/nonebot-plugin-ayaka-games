import re
from ayaka import *


def get_name(event: GroupMessageEvent):
    return event.sender.card if event.sender.card else event.sender.nickname


async def get_uid_name(bot: Bot, event: GroupMessageEvent, arg: str):
    '''arg: [CQ:at <uid>] | @用户名

    获取该事件所在群聊里，指定用户的uid、名称'''
    uid = 0
    name = ""

    r = re.search(r"\[CQ:at,qq=(?P<uid>\d+)\]", arg)
    if r:
        uid = int(r.group('uid'))
        data = await bot.get_group_member_info(group_id=event.group_id, user_id=uid)
        name: str = data['card'] if data['card'] else data['nickname']
        return uid, name

    r = re.search(r"@(?P<name>\w+)", arg)
    if r:
        name: str = r.group('name')
        data = await bot.get_group_member_list(group_id=event.group_id)
        for d in data:
            if d['card'] == name or d['nickname'] == name:
                uid: int = d['user_id']
                break

    return uid, name
