from ayaka import AyakaApp, AyakaUserDB
from .utils import UserInput, get_uid_name

app = AyakaApp("背包")
app.help = '''查看拥有财富'''


class UserMoney(AyakaUserDB):
    __table_name__ = "user_money"
    money: int = 1000

    @classmethod
    def get(cls, uid):
        return UserMoney.select_one(
            user_id=uid,
            group_id=app.group_id
        )

    def change(self, diff):
        self.money += diff
        self.save()
        return self.money


UserMoney.create_table()


@app.on.idle(True)
@app.on.command("bag", "背包")
async def show_bag(data: UserInput):
    # 有参数
    if data.value:
        uid, name = await get_uid_name(app, data)
        if not uid:
            await app.send("查无此人")
            return

    # 无参数
    else:
        name = app.user_name
        uid = app.user_id

    usermoney = UserMoney.get(uid)
    await app.send(f"[{name}]当前有 {usermoney.money}金")
