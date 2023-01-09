'''
    签到模块
'''
import datetime
from ayaka import AyakaBox, AyakaUserDB
from .bag import get_money
from .data import config

box = AyakaBox('签到')


class LastDate(AyakaUserDB):
    __table_name__ = "checkin"
    value: str = ""


@box.on_cmd(cmds=['checkin', '签到'], always=True)
async def checkin():
    last_date = LastDate.select_one(
        group_id=box.group_id,
        user_id=box.user_id
    )

    date = str(datetime.datetime.now().date())

    if date == last_date.value:
        await box.send(f"[{box.user_name}] 今天已经签到过了")
        return

    last_date.value = date

    # 签到奖励
    money = get_money(box.group_id, box.user_id)
    money.value += config.checkin_reward
    await box.send(f"[{box.user_name}] 签到成功，系统奖励 {config.checkin_reward}金")
    await box.send(f"[{box.user_name}] 当前拥有 {money.value}金")
