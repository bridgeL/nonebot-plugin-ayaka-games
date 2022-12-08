'''
    签到模块
'''
from pydantic import Field
from ayaka import AyakaApp, AyakaInput, AyakaUserDB, AyakaConfig
import datetime
from .bag import UserMoney

app = AyakaApp('签到')


class Config(AyakaConfig):
    __app_name__ = app.name
    reward_money: int = 10000


config = Config()


class LastDate(AyakaUserDB):
    __table_name__ = "checkin"
    last_date: str = ""


LastDate.create_table()


class UserInput(AyakaInput):
    number: int = Field(description="至少为0", ge=0)


@app.on.idle()
@app.on.command("修改签到奖励")
async def change_checkin(data: UserInput):
    uids = app.ayaka_root_config.owners + app.ayaka_root_config.admins
    if app.user_id not in uids:
        await app.send("仅ayaka所有者或管理者可以修改此数值")
        return

    config.reward_money = data.number
    await app.send("修改成功")


@app.on.idle()
@app.on.command('checkin', '签到')
async def checkin(last: LastDate, usermoney: UserMoney):
    date = str(datetime.datetime.now().date())
    name = app.user_name
    uid = app.user_id

    if date == last.last_date:
        await app.send(f"[{name}] 今天已经签到过了")
        return

    last.last_date = date
    last.save()

    # 签到奖励
    money = usermoney.change(config.reward_money)
    await app.send(f"[{name}] 签到成功，系统奖励 {config.reward_money}金")
    await app.send(f"[{name}] 当前拥有 {money}金")
