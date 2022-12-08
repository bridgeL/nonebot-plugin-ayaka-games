from pydantic import Field
from typing import Optional, Union
from ayaka import AyakaApp, AyakaInput, MessageSegment, msg_type


class UserInput(AyakaInput):
    value: Optional[Union[msg_type.T_At, int, str]] = Field(
        description="查询目标的QQ号/名称/@xx")

    def is_uid(self):
        return isinstance(self.value, (MessageSegment, int))

    def get_value(self):
        if isinstance(self.value, MessageSegment):
            return int(self.value.data["qq"])
        if isinstance(self.value, str) and self.value.startswith("@"):
            return self.value[1:]
        return self.value


async def get_uid_name(app: AyakaApp, data: UserInput):
    users = await app.bot.get_group_member_list(group_id=app.group_id)
    value = data.get_value()

    if data.is_uid():
        for user in users:
            uid = user["user_id"]
            if uid == value:
                name = user["card"] or user["nickname"]
                return uid, name
        return 0, ""
    else:
        for user in users:
            name = user["card"] or user["nickname"]
            if name == value:
                uid = user["user_id"]
                return uid, name
        return 0, ""
