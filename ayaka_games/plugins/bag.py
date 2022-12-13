from ayaka import AyakaApp, AyakaUserDB
from ayaka.extension import UserInput

app = AyakaApp("背包")
app.help = '''查看拥有财富'''


class UserMoneyData(AyakaUserDB):
    '''用户金钱'''
    __table_name__ = "user_money"
    money: int = 1000

    @classmethod
    def get(cls, uid):
        return UserMoneyData.select_one(
            user_id=uid,
            group_id=app.group_id
        )

    def change(self, diff):
        self.money += diff
        return self.money


@app.on.idle(True)
@app.on.command("bag", "背包")
async def show_bag(data: UserInput):
    # 有参数
    if data.user:
        name = data.user.name
        uid = data.user.id
    # 无参数
    else:
        name = app.user_name
        uid = app.user_id
    usermoney = UserMoneyData.get(uid)
    await app.send(f"[{name}]当前有 {usermoney.money}金")
