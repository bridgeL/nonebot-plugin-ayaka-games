'''
    签到模块
'''
from ayaka import AyakaApp
import datetime
from .user_bag import change_money

app = AyakaApp('签到')
app.help = '''签到
- 签到/checkin
'''


@app.on_command(['checkin', '签到'])
async def checkin():
    # 判断是否签到过，结果保存到本地
    file = app.group_storage(f"{app.user_id}.txt", default="")
    _date = file.load()
    date = str(datetime.datetime.now().date())
    name = app.user_name

    if date == _date:
        await app.send(f"[{name}] 今天已经签到过了")
        return

    file.save(date)

    # 签到奖励
    money = change_money(app.user_id, 10000)
    await app.send(f"[{name}] 签到成功，系统奖励 10000金")
    await app.send(f"[{name}] 当前拥有 {money}金")
