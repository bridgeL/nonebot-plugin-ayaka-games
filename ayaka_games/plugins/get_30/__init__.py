'''
    抢30
'''
from asyncio import sleep
from random import randint
from typing import List

from pydantic import Field
from ayaka import AyakaApp, AyakaInputModel

app = AyakaApp("抢30")
app.help = '''
至少2人游玩，一局内进行多轮叫牌，谁最先达到或超过30点谁获胜
总共52张牌，直到全部用完后才会洗牌，只要不退出游戏，下局的牌库将继承上局
首轮所有人筹码为10，每轮所有人筹码+1
'''


class NumInput(AyakaInputModel):
    number: int = Field(description="至少为0", ge=0)


class Player:
    def __init__(self, uid: int, name: str) -> None:
        self.uid = uid
        self.name = name

        self.money = 0
        self.quote = 0
        self.score = 0
        self.win_cnt = 0
        self.first = False

    def quote_win(self, card: int):
        self.money -= self.quote
        self.score += card


def shuffle(array: list):
    result = []
    while array:
        i = randint(0, len(array)-1)
        result.append(array.pop(i))
    return result


class Game:
    def __init__(self) -> None:
        self.players: List[Player] = []
        self.cards = []
        self.first = -1
        self.i = 0
        self.card = 0
        self.last_quote = -1

    @property
    def player_cnt(self):
        return len(self.players)

    def get_player(self, uid: int):
        for p in self.players:
            if p.uid == uid:
                return p

    def join(self, uid: int, name: str):
        p = self.get_player(uid)
        if p:
            return False, f"[{p.name}] 已在房间中"
        p = Player(uid, name)
        self.players.append(p)
        return True, f"[{p.name}] 加入房间"

    def leave(self, uid: int):
        p = self.get_player(uid)
        if not p:
            return False, f"({uid}) 不在房间中"
        self.players.remove(p)
        return True, f"[{p.name}] 离开房间"

    def refresh_cards(self):
        if not self.cards:
            self.cards = shuffle([i+1 for i in range(13) for j in range(4)])

    @property
    def player_now(self):
        i = (self.first+self.i) % self.player_cnt
        return self.players[i]

    def refresh_card(self):
        self.refresh_cards()
        self.card = self.cards.pop()

    def start(self):
        if self.player_cnt < 2:
            return False, "至少需要2人才能开始游戏"

        # 初始化状态
        for p in self.players:
            p.money = 9
            p.quote = -1
            p.score = 0
            p.first = False

        return True, "游戏开始"

    def round_begin(self):
        for p in self.players:
            p.quote = -1
            p.money += 1
            p.first = False

        self.first = (self.first+1) % self.player_cnt
        self.i = 0
        self.last_quote = -1
        self.refresh_card()
        self.player_now.first = True

    @property
    def round_is_end(self):
        return self.i >= self.player_cnt

    def quote(self, uid: int, quote: int):
        # 参数校验
        if not self.get_player(uid):
            return False, f"({uid}) 没有加入游戏"

        # 没轮到你
        p = self.player_now
        if p.uid != uid:
            return False, f"没轮到你"

        if quote != 0 and quote <= self.last_quote:
            return False, f"至少大于{self.last_quote}，或者0放弃"

        if quote > p.money:
            return False, "你没有那么多钱"

        p.quote = quote
        self.last_quote = quote
        self.i += 1
        return True, f"[{p.name}] 报价 [{quote}]"

    def settle(self):
        ps = [p for p in self.players]

        # 取最高者
        ps.sort(key=lambda p: p.quote, reverse=True)
        p = ps[0]

        # 庄家赚了
        if p.quote == 0:
            p = self.players[self.first]

        # 赢得此牌
        p.quote_win(self.card)
        return f"[{p.name}] 赢得此牌"

    @property
    def winner(self):
        for p in self.players:
            if p.score >= 30:
                return p

    @property
    def card_info(self):
        return f"当前牌 {self.card}"

    @property
    def player_info(self):
        items = []
        items.append("报价 筹码 点数 玩家名")
        for p in self.players:
            if p.quote >= 0:
                quote = p.quote
            else:
                quote = "无"

            if p == self.player_now:
                prefix = ">"
            else:
                prefix = "-"

            items.append(
                f"{prefix}  {quote}  {p.money}  {p.score}  [{p.name}]")
        return "\n".join(items)

    @property
    def room_info(self):
        items = ["房间成员："]
        for p in self.players:
            if p.win_cnt:
                win = f"获胜{p.win_cnt}局"
            else:
                win = ""
            items.append(f"[{p.name}] {win}")
        return "\n".join(items)


@app.on.idle()
@app.on.command("抢30")
async def app_entrance():
    '''打开游戏'''
    await app.start()
    await app.send(app.help)
    await app.goto("room")
    await app.send(app.help)

    game = Game()
    app.cache.game = game
    f, info = game.join(app.user_id, app.user_name)
    await app.send(info)


@app.on.state("room")
@app.on.command("exit", "退出")
async def exit_room():
    '''关闭游戏'''
    await app.close()


@app.on.state("play")
@app.on.command("exit", "退出")
async def exit_play():
    '''退出游戏'''
    await app.send("游戏已开始，你确定要终结游戏吗？请使用命令：强制退出")


@app.on.state("room")
@app.on.command("join", "加入")
async def join():
    '''加入房间'''
    game: Game = app.cache.game
    f, info = game.join(app.user_id, app.user_name)
    await app.send(info)


@app.on.state("room")
@app.on.command("leave", "离开")
async def leave():
    '''离开房间'''
    game: Game = app.cache.game
    f, info = game.leave(app.user_id)
    await app.send(info)

    if f and game.player_cnt == 0:
        await app.close()


@app.on.state("room")
@app.on.command("start", "begin", "开始")
async def start():
    '''开始游戏'''
    game: Game = app.cache.game
    f, info = game.start()
    await app.send(info)

    # 启动失败
    if not f:
        return

    await app.goto("play")
    game.round_begin()
    await app.send(game.card_info)
    await app.send(game.player_info)


@app.on.state("room")
@app.on.command("info", "信息")
async def room_info():
    '''展示房间信息'''
    game: Game = app.cache.game
    await app.send(game.room_info)


@app.on.state("play")
@app.on.command("info", "信息")
async def play_info():
    '''展示当前牌、所有人筹码、报价'''
    game: Game = app.cache.game
    await app.send(game.card_info)
    await app.send(game.player_info)


@app.on.state("play")
@app.on.text()
@app.on_model(NumInput)
async def quote():
    '''报价叫牌，要么为0，要么比上一个人高，如果全员报价为0，则本轮庄家获得该牌'''
    game: Game = app.cache.game
    data: NumInput = app.model_data
    num = data.number
    f, info = game.quote(app.user_id, num)

    # 报价失败
    if not f:
        await app.send(info)
        return

    await app.send(game.player_info)

    # 本轮是否结束
    if not game.round_is_end:
        return

    # 结算时公布报价结果
    info = game.settle()
    await app.send(info)

    p = game.winner
    if not p:
        await sleep(2)
        game.round_begin()
        await app.send("下一轮\n所有人筹码+1\n" + game.card_info)
        await app.send(game.player_info)
        return

    await app.send(game.player_info)
    await app.send(f"[{p.name}] 获胜")
    await sleep(2)
    p.win_cnt += 1

    # 返回房间
    await app.goto("room")
    await app.send(game.room_info)
    await app.send("发送start开始下一局")
