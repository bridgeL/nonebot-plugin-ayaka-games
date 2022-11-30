'''
    签到模块
'''
from ayaka import AyakaApp
import datetime
from ..bag import change_money

app = AyakaApp('签到')

class Config(app.BaseConfig):
    reward_money: int = 10000


config = Config()


def ensure_key_is_int(data: dict):
    data = {int(k): v for k, v in data.items()}
    return data


@app.on.idle()
@app.on.command('修改签到奖励金额')
async def change_checkin():
    '''<num>'''
    uids = app.ayaka_root_config.owners + app.ayaka_root_config.admins
    if app.user_id not in uids:
        await app.send("仅ayaka所有者或管理者可以修改此数值")
        return

    try:
        config.reward_money = int(str(app.args[0]))
        await app.send("修改成功")
    except:
        await app.send("设置失败")
        return


@app.on.idle()
@app.on.command('checkin', '签到')
async def checkin():
    ''' '''
    # 判断是否签到过，结果保存到本地
    file = app.storage.group_path().json("date.json", {})
    data = file.load()
    data = ensure_key_is_int(data)
    _date = data.get(app.user_id, "")
    date = str(datetime.datetime.now().date())
    name = app.user_name

    if date == _date:
        await app.send(f"[{name}] 今天已经签到过了")
        return

    data[app.user_id] = date
    file.save(data)

    # 签到奖励
    money = change_money(app.user_id, config.reward_money)
    await app.send(f"[{name}] 签到成功，系统奖励 {config.reward_money}金")
    await app.send(f"[{name}] 当前拥有 {money}金")
