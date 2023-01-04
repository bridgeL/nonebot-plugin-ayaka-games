'''
    签到模块
'''
import datetime
from ayaka import AyakaConfig, AyakaBox, AyakaUserDB, slow_load_config
from .bag import get_money

box = AyakaBox('签到')


@slow_load_config
class Config(AyakaConfig):
    __config_name__ = box.name
    reward_money: int = 10000


class LastDate(AyakaUserDB):
    __table_name__ = "checkin"
    value: str = ""


@box.on_cmd(cmds=['checkin', '签到'])
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
    config = Config()
    money.value += config.reward_money
    await box.send(f"[{box.user_name}] 签到成功，系统奖励 {config.reward_money}金")
    await box.send(f"[{box.user_name}] 当前拥有 {money.value}金")
