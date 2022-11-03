import re
from ayaka import MessageSegment, Bot


def str_to_int(num_str: str):
    r = re.search(r"^\d+$", str(num_str))
    if r:
        return int(r.group())


class GroupUserFinder:
    def __init__(self, bot: Bot, group_id: int) -> None:
        self.bot = bot
        self.group_id = group_id

    async def get_all_users(self):
        return await self.bot.get_group_member_list(group_id=self.group_id)

    async def get_user_by_id(self, uid: int):
        users = await self.get_all_users()
        for user in users:
            if user["user_id"] == uid:
                return user

    async def get_user_by_name(self, name: str):
        users = await self.get_all_users()
        for user in users:
            _name = user["card"] or user["nickname"]
            if _name == name:
                return user

    async def get_user_by_at(self, at: MessageSegment):
        users = await self.get_all_users()
        uid = int(at.data["qq"])
        return await self.get_user_by_id(uid)

    async def get_user_by_segment(self, msg: MessageSegment):
        if msg.type == "at":
            return await self.get_user_by_at(msg)

        msg_str = str(msg)
        if msg_str.startswith("@"):
            return await self.get_user_by_name(msg_str[1:])

        user = await self.get_user_by_name(msg_str)
        if user:
            return user

        r = re.search(r"^\d+$", msg_str)
        if r:
            uid = int(msg_str)
            return await self.get_user_by_id(uid)
