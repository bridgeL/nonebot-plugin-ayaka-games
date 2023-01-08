from ayaka import AyakaBox, get_user, AyakaUserDB

box = AyakaBox("背包")


class Money(AyakaUserDB):
    __table_name__ = "money"
    value: int = 1000


def get_money(group_id: int, user_id: int):
    return Money.select_one(
        group_id=group_id,
        user_id=user_id
    )


@box.on_cmd(cmds=["bag", "背包"], always=True)
async def show_bag():
    '''展示背包；你还可以 bag @xx 查看其他人的背包'''
    if not box.arg:
        money = get_money(box.group_id, box.user_id)
        name = box.user_name
    else:
        users = await box.bot.get_group_member_list(group_id=box.group_id)
        user = get_user(box.arg[0], users)
        if not user:
            await box.send("查无此人")
            return
        money = get_money(box.group_id, user.id)
        name = user.name

    await box.send(f"[{name}]当前有 {money.value}金")
