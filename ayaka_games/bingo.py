'''
bingo 小游戏
'''
from random import randint, seed
from time import time
from .user_bag import change_money
from ayaka import AyakaApp

app = AyakaApp("bingo")
app.help = '''经典小游戏
- b <数字> 花费100金打开一张卡，当卡片练成一整行、一整列或一整条对角线时，获得200*n金的奖励
- bb <数字> 免费生成一张新的bingo表，默认大小为4
'''

seed(time())


class Bingo:
    def __init__(self, n) -> None:
        self.n = n
        self.build()

    def build(self):
        n = self.n
        self.data = [1 for i in range(n*n)]
        self.opened = [0 for i in range(n*n)]
        self.ok = False
        i = 0
        while True:
            paths = self.get_win_paths()
            if len(paths) == 1:
                break

            # 回退上一操作
            if not paths:
                self.data[i] = 1

            i = randint(0, n*n-1)
            while not self.data[i]:
                i = randint(0, n*n-1)

            self.data[i] = 0

    def get_win_paths(self):
        n = self.n

        paths = []

        # 行
        for i in range(n):
            path = [i*n+j for j in range(n)]
            if all(self.data[k] for k in path):
                paths.append(path)

        # 列
        for i in range(n):
            path = [j*n+i for j in range(n)]
            if all(self.data[k] for k in path):
                paths.append(path)

        # 对角
        path = [i*n+i for i in range(n)]
        if all(self.data[k] for k in path):
            paths.append(path)

        path = [i*n+n-i-1 for i in range(n)]
        if all(self.data[k] for k in path):
            paths.append(path)

        return paths

    def check_win(self):
        path = self.get_win_paths()[0]
        return all(self.opened[k] for k in path)

    def get_all_info(self):
        n = self.n
        info = ""
        for i in range(n):
            for j in range(n):
                s = self.get(i*n+j)

                info += f"[{s}] "
            info = info[:-1] + "\n"
        return info[:-1]

    def get(self, i):
        return "⚪" if self.data[i] else "❌"

    def get_info(self):
        n = self.n
        info = ""
        for i in range(n):
            for j in range(n):
                k = i*n+j
                if not self.opened[k]:
                    s = str(k)
                else:
                    s = self.get(k)

                info += f"[{s}] "
            info = info[:-1] + "\n"
        return info[:-1]

    def open(self, i):
        if self.ok:
            return False, "已无奖励"

        n = self.n
        if i >= n*n or i < 0:
            return False, "超出范围"

        if self.opened[i]:
            return False, "已被翻开"

        d = self.get(i)
        self.opened[i] = 1

        if self.check_win():
            self.ok = True

        return True, d


@ app.on_command("bb")
async def handle():
    try:
        n = int(str(app.args[0]))
        if n < 3 or n > 6:
            raise
    except:
        n = 4
        await app.send("参数不合法，采用默认值4")

    bingo = app.cache.bingo
    if not isinstance(bingo, Bingo):
        bingo = Bingo(n)
        app.cache.bingo = bingo
    else:
        bingo.n = n
        bingo.build()
    await app.send(bingo.get_info())
    # await app.send(bingo.get_all_info())


@ app.on_command(["bingo", "b"])
async def handle():
    bingo = app.cache.bingo
    if not isinstance(bingo, Bingo):
        bingo = Bingo(4)
        app.cache.bingo = bingo
        await app.send("bingo不存在，已自动生成")

    if not app.args:
        await app.send(bingo.get_info())
        await app.send(app.help)
        return

    try:
        n = int(str(app.args[0]))
    except:
        await app.send("参数错误")
        return

    f, info = bingo.open(n)
    if not f:
        await app.send(info)
        return

    money = change_money(-100, app.user_id)
    if bingo.ok:
        money = change_money(bingo.n*200, app.user_id)
        await app.send(f"[{app.user_name}] 赢了，奖励 {bingo.n*200}金，当前拥有 {money}金")
        await app.send(bingo.get_all_info())
    else:
        await app.send(f"[{app.user_name}] 花费100金翻开了{n}号： {info}")
        await app.send(bingo.get_info())
