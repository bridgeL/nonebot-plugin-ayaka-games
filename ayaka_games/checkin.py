'''
    签到模块
'''
from ayaka import *
from .utils.time import get_time_s

# 跨插件引用
from .bag import add_money
from .utils.name import get_name


app = AyakaApp('checkin', only_group=True)
app.help = "签到"


@app.on_command(['checkin', '签到'])
async def checkin():
    name = get_name(app.event)

    # 判断是否签到过，结果保存到本地
    sa = app.storage.accessor(app.event.user_id)
    date = get_time_s("%Y-%m-%d")
    if date == sa.get(""):
        await app.send(f"[{name}] 今天已经签到过了")
        return
    sa.set(date)

    # 签到奖励 
    money = add_money(100, app.device, app.event.user_id)
    await app.send(f"[{name}] 签到成功，系统奖励 200000金")
    await app.send(f"[{name}] 当前拥有 {money}金")
