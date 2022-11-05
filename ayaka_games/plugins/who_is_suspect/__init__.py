'''
    谁是卧底？
'''
from random import choice, randint
from typing import List
from ayaka import AyakaApp, MessageSegment
from .utils import str_to_int, GroupUserFinder

app = AyakaApp("谁是卧底")
app.help = {
    "init": '''
至少4人游玩，游玩前请加bot好友，否则无法通过私聊告知关键词
参与玩家的群名片不要重名，否则会产生非预期的错误=_=||
卧底只有一个
''',
    "room": "房间已建立，正在等待玩家加入...",
    "play": "游戏正在进行中..."
}


data = app.storage.plugin_path().file("data.txt", "TEST test").load()
data = data.strip().split("\n")
words_list = [d.split(" ", 1) for d in data]


class Player:
    def __init__(self, uid: int, name: str) -> None:
        self.uid = uid
        self.name = name
        self.word = ""
        self.num = 0

        self.vote_cnt = 0
        self.vote_to: Player = None
        self.is_suspect = False
        self.out = False

    def __str__(self):
        return f"[{self.name}]"

    def clear(self):
        self.vote_cnt = 0
        self.vote_to = None
        self.is_suspect = False
        self.out = False

    def set_normal(self, word: str):
        self.clear()
        self.word = word

    def set_suspect(self, word: str):
        self.clear()
        self.word = word
        self.is_suspect = True

    def clear_vote(self):
        self.vote_to = None
        self.vote_cnt = 0

    @property
    def state(self):
        if self.out:
            return f"[{self.name}] 出局"

        if self.vote_to:
            return f"[{self.name}] 已投"

        return f"[{self.name}] 未投"


class Game:
    def __init__(self) -> None:
        self.players: List[Player] = []

    @property
    def player_cnt(self):
        return len(self.players)

    @property
    def no_out_players(self):
        return [p for p in self.players if not p.out]

    @property
    def voted_end(self):
        if all(p.vote_to for p in self.no_out_players):
            return True

        # 或者有人已获得半数以上的票数
        cnt = int(len(self.no_out_players)/2)
        for p in self.no_out_players:
            if p.vote_cnt > cnt:
                return True

    @property
    def players_state(self):
        items = ["投票情况："]
        items.extend(p.state for p in self.players)
        return "\n".join(items)

    @property
    def vote_info(self):
        items = ["得票情况："]
        items.extend(
            f"[{p.num}] [{p.name}] {p.vote_cnt}" for p in self.no_out_players)
        return "\n".join(items)

    @property
    def room_info(self):
        items = ["房间成员："]
        items.extend(str(p) for p in self.players)
        return "\n".join(items)

    def get_player(self, uid: int):
        for p in self.players:
            if p.uid == uid:
                return p

    def join(self, uid: int, name: str):
        p = self.get_player(uid)
        if p:
            return False, f"{p} 已在房间中"
        p = Player(uid, name)
        self.players.append(p)
        return True, f"{p} 加入房间"

    def leave(self, uid: int):
        p = self.get_player(uid)
        if not p:
            return False, f"({uid}) 不在房间中"
        self.players.remove(p)
        return True, f"{p} 离开房间"

    def get_words(self):
        normal, fake = choice(words_list)

        # 有可能翻转
        if randint(0, 1):
            normal, fake = fake, normal

        return normal, fake

    def start(self):
        if self.player_cnt < 4:
            return False, "至少需要4人才能开始游戏"

        normal, fake = self.get_words()

        # 初始化状态
        for i, p in enumerate(self.players):
            p.set_normal(normal)
            p.num = i+1

        # 随机卧底
        i = randint(0, self.player_cnt - 1)
        self.players[i].set_suspect(fake)

        return True, "游戏开始"

    def vote(self, uid: int, vote_to_uid: int):
        # 参数校验
        src = self.get_player(uid)
        if not src:
            return False, f"({uid}) 没有加入游戏"

        obj = self.get_player(vote_to_uid)
        if not obj:
            return False, f"({vote_to_uid}) 没有加入游戏"

        # 不可重投
        if src.vote_to:
            return False, f"{src} 已经投票过了"

        # 已出局的不能投票
        if src.out:
            return False, f"{src} 已经出局了"

        # 不能投给已出局的
        if obj.out:
            return False, f"{obj} 已经出局了"

        src.vote_to = obj
        obj.vote_cnt += 1
        return True, f"{src} 投票给了 {obj}"

    def kickout(self):
        info = self.vote_info + "\n\n"
        ps = self.no_out_players

        # 取最高者
        ps.sort(key=lambda p: p.vote_cnt, reverse=True)
        vote_cnt = ps[0].vote_cnt
        for i, p in enumerate(ps):
            if p.vote_cnt < vote_cnt:
                ps = ps[:i]
                break

        # 清理本轮投票
        for p in self.no_out_players:
            p.clear_vote()

        # 只票出一人，正常结算
        if len(ps) == 1:
            p = ps[0]
            p.out = True
            info += f"{p} 出局！"
            return True, info

        # 平票
        info += "平局！"
        return False, info

    def check_end(self):
        for p in self.players:
            if p.is_suspect and p.out:
                return True, "普通人赢了！"
        if len(self.no_out_players) <= 2:
            return True, "卧底赢了！"
        return False, ""

    def conclude(self):
        ps = [p for p in self.players if not p.is_suspect]
        word = ps[0].word

        items = []
        items.append(f"普通人的关键词： {word}")
        items.append(" ".join(str(p) for p in ps) + " 是普通人！")

        for p in self.players:
            if p.is_suspect:
                break

        items.append(f"卧底的关键词： {p.word}")
        items.append(f"{p} 是卧底！")
        return "\n".join(items)


async def get_uid(arg: MessageSegment):
    users = await app.bot.get_group_member_list(group_id=app.group_id)

    # at？
    if arg.type == "at":
        at = arg
        try:
            uid = int(at.data["qq"])
        except:
            return

        for user in users:
            if user["user_id"] == uid:
                return user["user_id"]
        return

    # 名称？
    name = str(arg)
    if name.startswith("@"):
        name = name[1:]

    for user in users:
        _name = user["card"] or user["nickname"]
        if _name == name:
            return user["user_id"]


async def check_friend(uid: int):
    users = await app.bot.get_friend_list()
    for user in users:
        if user["user_id"] == uid:
            return True


@app.on.idle()
@app.on.command("谁是卧底")
async def app_entrance():
    '''打开应用'''
    if not await app.start():
        return

    await app.send(app.help)
    app.state = "room"
    await app.send(app.help)

    app.cache.game = Game()
    await join()


@app.on.state("room")
@app.on.command("exit", "退出")
async def exit_room():
    '''关闭游戏'''
    await app.close()


@app.on.state("play")
@app.on.command("exit", "退出")
async def exit_play():
    await app.send("游戏已开始，你确定要终结游戏吗？请使用命令：强制退出")


@app.on.state("room")
@app.on.command("join", "加入")
async def join():
    '''加入房间'''
    # 校验好友
    if not await check_friend(app.user_id):
        await app.send("只有bot的好友才可以加入房间，因为游戏需要私聊关键词")
        return

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

    app.state = "play"
    for p in game.players:
        await app.bot.send_private_msg(user_id=p.uid, message=p.word)


@app.on.state("room")
@app.on.command("info", "信息")
async def room_info():
    '''展示房间内成员列表'''
    game: Game = app.cache.game
    await app.send(game.room_info)


@app.on.state("play")
@app.on.command("info", "信息")
async def play_info():
    '''展示投票情况'''
    game: Game = app.cache.game
    await app.send(game.players_state)
    await app.send(game.vote_info)


@app.on.state("play")
@app.on.command("vote", "投票")
async def vote():
    '''请at你要投票的对象，一旦投票无法更改'''
    game: Game = app.cache.game

    # 验证参数
    if not app.args:
        await app.send("没有获取到有效参数")
        return

    num = str_to_int(str(app.args[0]))
    if num is not None:
        num -= 1
        if num < 0 or num >= game.player_cnt:
            await app.send("没有获取到有效参数")
            return

        uid = game.players[num].uid

    else:
        group_user_finder = GroupUserFinder(app.bot, app.group_id)
        user = await group_user_finder.get_user_by_segment(app.args[0])
        if not user:
            await app.send("没有获取到有效参数")
            return

        uid = user["user_id"]

    # 投票
    f, info = game.vote(app.user_id, uid)
    await app.send(info)

    # 投票失败
    if not f:
        return

    # 投票是否结束
    if not game.voted_end:
        return

    # 结算时公布投票结果
    f, info = game.kickout()
    await app.send(info)

    # 出现平局
    if not f:
        return

    # 成功踢出一人，判断游戏是否结束
    f, info = game.check_end()
    if not f:
        await app.send("游戏继续！")
        return

    # 展示结果
    await app.send(game.conclude())
    await app.send(info)

    # 返回房间
    app.state = "room"
    await app.send("已回到房间，可发送start开始下一局")
