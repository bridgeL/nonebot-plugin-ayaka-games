from ayaka import AyakaBox, get_user, AyakaUserDB, on_command

box = AyakaBox("背包")


class Money(AyakaUserDB):
    __table_name__ = "money"
    value: int = 1000


def get_money(group_id: int, user_id: int):
    return Money.select_one(
        group_id=group_id,
        user_id=user_id
    )


matcher = on_command("bag", aliases={"背包"})


@matcher.handle()
async def show_bag():
    if not box.arg:
        money = get_money(box.group_id, box.user_id)
    else:
        users = await box.bot.get_group_member_list(group_id=box.group_id)
        user = get_user(box.arg[0], users)
        if not user:
            await box.send("查无此人")
            return
        money = get_money(box.group_id, user.id)

    await box.send(f"[{box.user_name}]当前有 {money.value}金")
