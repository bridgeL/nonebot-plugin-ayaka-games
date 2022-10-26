'''
    +1s 

    使用app.group_storage永久保存数据到本地

    使用app.cache快速存取数据，但是app.cache中的对象会在bot重启后丢失
'''
from asyncio import sleep
from random import choice
from typing import Dict
from ayaka import AyakaApp

app = AyakaApp("加一秒")
app.help = '''
每人初始时间值为0
每有3个不同的人执行一次或若干次加1，boss就会完成蓄力，吸取目前时间值最高的人的时间，如果有多人，则均吸取1点
boss时间值>=10时，游戏结束，时间值<=boss的人中，时间值最高的人获胜，一切重置
- 加一秒 启动游戏
- exit/退出 退出游戏（数据保留）

游戏内指令：
- +1 让你的时间+1
- 我的 查看你目前的时间
- boss 查看boss的时间和能量
- 全部 查看所有人参与情况，以及boss的时间和能量
'''

feelings = [
    "感觉身体被掏空",
    "感受到一阵空虚",
    "的时间似乎变快了",
    "似乎被夺走了什么东西"
]

restarts = [
    "世界被虚空的狂风撕碎",
    "世界在不灭的火焰中湮灭",
    "&*@）#……游戏出故障了",
    "限界的界世了越超间时的ssob"
]


async def get_user_data():
    users = await app.bot.get_group_member_list(group_id=app.group_id)
    user_data = {u["user_id"]: u["card"] or u["nickname"] for u in users}
    return user_data


def get_max(data: Dict[int, int]):
    '''
        data 是保存了 uid-time 数据的字典
    '''
    # 转换为items列表，方便排序
    items = list(data.items())
    items.sort(key=lambda x: x[1], reverse=True)

    uids = []
    if not items:
        return uids

    time_max = items[0][1]
    for uid, time in items:
        if time == time_max:
            uids.append(uid)
        else:
            break

    return uids


class PlayerGroup:
    def __init__(self) -> None:
        # 获得AyakaStorage
        # 如果给定了default，那么在load时，若文件不存在，会写入default作为初始值
        self.storage = app.group_storage("time.json", default={})
        self.load()

    def load(self):
        # 加载数据，如果不存在文件，则自动创建
        data: dict = self.storage.load()
        # json.load时，得到的key都是str类型，因此需要转换
        self.data = {int(uid): time for uid, time in data.items()}

    def save(self):
        # 保存数据
        # 如果是json文件，则data在写入时会自动通过json.dumps转换
        # 如果是txt文件，则data只能是str类型
        self.storage.save(self.data)

    def get_time(self, uid: int) -> int:
        '''获取uid对应的时间值'''

        # 如果不存在则设置默认值，并保存
        if uid not in self.data:
            self.data[uid] = 0
            self.save()
            return 0

        # 存在则返回
        return self.data[uid]

    def change_time(self, uid: int, diff: int):
        '''获取uid对应的时间值，如果不存在，返回为0'''

        time: int = self.data.get(uid, 0)

        # 修改time
        time += diff

        # 保存
        self.data[uid] = time
        self.save()

        # 返回修改后的值
        return time

    def clear_all(self):
        self.data = {}
        self.save()


class Boss:
    boss_default = {
        "time": 0,
        # 记录不同的人的发言
        "uids": []
    }

    max_time = 10
    max_power = 3

    def __init__(self, player_group: PlayerGroup) -> None:
        # 获得AyakaStorage
        self.storage = app.group_storage(
            "boss.json",
            default=self.boss_default
        )
        self.load()
        self.player_group = player_group

    def load(self):
        # 加载数据
        self.data = self.storage.load()

    def save(self):
        self.storage.save(self.data)

    @property
    def time(self) -> int:
        return self.data["time"]

    @time.setter
    def time(self, v: int):
        self.data["time"] = v
        self.save()

    @property
    def power(self):
        return len(self.data["uids"])

    def clear_power(self):
        self.data["uids"] = []
        self.save()

    def add_power(self, uid: int):
        # 防止重复
        uids: list = self.data["uids"]
        if uid in uids:
            return
        uids.append(uid)
        self.data["uids"] = uids
        self.save()

    def kill(self, data: dict):
        '''
            data 是保存了 uid-time 数据的字典
        '''
        # 发动攻击，清除power
        self.clear_power()

        # 记录吸取情况
        uids = get_max(data)

        # 吸取时间
        for uid in uids:
            self.player_group.change_time(uid, -1)
        self.time += len(uids)

        # 告知吸取情况
        return uids

    @property
    def state(self):
        info = f"boss目前的时间：{self.time}/{self.max_time}\nboss目前的能量：{self.power}/{self.max_power}"
        if self.power >= self.max_power - 1:
            info += "\nboss即将发动攻击！"
        if self.time >= self.max_time - 1:
            info += "\nboss的时间即将到达顶峰！"
        return info


class Game:
    def __init__(self) -> None:
        self.player_group = PlayerGroup()
        self.boss = Boss(self.player_group)

    def get_winners(self):
        boss_time = self.boss.time
        data = self.player_group.data
        # 时间值小于等于boss的人
        data = {uid: time for uid, time in data.items() if time <= boss_time}
        return get_max(data)


@app.on_command("加一秒")
async def _():
    await app.start()
    await app.send(app.help)
    app.cache.game = Game()


@app.on_state_command(["exit", "退出"])
async def _():
    await app.send("数据已保存")
    await app.close()


@app.on_state_command("我的")
async def inquiry():
    game: Game = app.cache.game
    time = game.player_group.get_time(app.user_id)
    await app.send(f"[{app.user_name}]目前的时间：{time}")


@app.on_state_command("boss")
async def inquiry_boss():
    game: Game = app.cache.game
    await app.send(game.boss.state)


@app.on_state_command("全部")
async def inquiry_boss():
    game: Game = app.cache.game

    # boss
    info = game.boss.state

    # 所有人
    data = game.player_group.data

    if not data:
        await app.send(info)
        return

    # 查找名字
    user_data = await get_user_data()

    for uid, time in data.items():
        info += f"\n[{user_data[uid]}]目前的时间：{time}"
    await app.send(info)


@app.on_state_command(["加1", "加一", "+1", "+1s"])
async def plus():
    game: Game = app.cache.game

    # 玩家
    time = game.player_group.change_time(app.user_id, 1)
    await app.send(f"[{app.user_name}]的时间增加了！目前为：{time}")

    # boss
    game.boss.add_power(app.user_id)
    await app.send(game.boss.state)

    if game.boss.power < game.boss.max_power:
        return

    # boss 攻击
    uids = game.boss.kill(game.player_group.data)

    await app.send("boss发动了攻击...")
    await sleep(2)
    await app.send("...")
    await sleep(2)

    if not uids:
        await app.send("无事发生")
        return

    # 查找名字
    user_data = await get_user_data()

    # 告知被攻击情况
    items = [f"[{user_data[uid]}] {choice(feelings)}" for uid in uids]
    await app.send("\n".join(items))

    if game.boss.time < game.boss.max_time:
        return

    # 游戏结束，告知胜利者
    uids = game.get_winners()

    await sleep(2)
    await app.send(f"boss的时间超越了世界的界限，{choice(restarts)}...")
    await sleep(2)
    await app.send("...")
    await sleep(2)

    items = [f"[{user_data[uid]}]" for uid in uids]
    info = "在上一个世界中：" + "、".join(items) + " 是最终的赢家！"
    await app.send(info)

    game.player_group.clear_all()
    game.boss.time = 0
