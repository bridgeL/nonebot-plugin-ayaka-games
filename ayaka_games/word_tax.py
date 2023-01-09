from random import sample
from time import time
from ayaka import AyakaBox, AyakaUserDB, AyakaGroupDB, AyakaDB, BaseModel, Bot, GroupMessageEvent, Field, load_data_from_file
from .bag import get_money, Money
from .data import downloader, config

box = AyakaBox("文字税")


words: list[str] = []


@downloader.on_finish
async def finish():
    path = downloader.BASE_DIR / "文字税.txt"
    words.extend(load_data_from_file(path))


class UserWord(AyakaUserDB):
    __table_name__ = "word_tax"
    word: str = Field(extra=AyakaDB.__primary_key__)
    uname: str = ""
    time: int = 0


class GroupWord(AyakaGroupDB):
    __table_name__ = "word_tax_group"
    words: str = ""


class GroupMarket(BaseModel):
    time: int = 0
    words: list[str] = []
    users: list[UserWord] = []
    first: bool = True

    def __init__(self, **data) -> None:
        super().__init__(**data)
        self.load(box.group_id)

    def load(self, group_id):
        if self.first:
            self.first = False
            self.users = UserWord.select_many(group_id=group_id)
            if self.users:
                self.time = self.users[0].time
                words = GroupWord.select_one(group_id=group_id).words
                self.words = [u for u in words]

    def refresh(self, group_id):
        self.first = False
        self.time = int(time())
        self.words = sample(words, 20)
        GroupWord.select_one(group_id=group_id).words = "".join(self.words)
        self.users = []
        UserWord.delete(
            group_id=group_id
        )

    def is_open(self):
        return int(time()) - self.time <= config.word_tax.open_duration

    def is_valid(self):
        return int(time()) - self.time <= config.word_tax.valid_duration

    def buy(self, group_id, user_id, uname):
        UserWord.delete(
            group_id=group_id,
            user_id=user_id,
        )
        self.users = [
            u for u in self.users
            if u.group_id != group_id or u.user_id != user_id
        ]
        words = sample(self.words, 3)
        users = [
            UserWord(
                group_id=group_id,
                user_id=user_id,
                word=word,
                time=self.time,
                uname=uname
            )
            for word in words
        ]
        UserWord.insert_many(users)
        self.users.extend(users)
        return words

    def check(self, msg: str, user_id: int):
        check_dict: dict[str, list[UserWord]] = {}
        for u in self.users:
            if u.user_id == user_id:
                break
        else:
            # 排除没抽的人
            return {}

        for u in self.users:
            if u.user_id == user_id:
                continue
            if u.word not in check_dict:
                check_dict[u.word] = [u]
            else:
                check_dict[u.word].append(u)

        _check_dict: dict[str, list[UserWord]] = {}
        for m in msg:
            if m not in _check_dict and m in check_dict:
                _check_dict[m] = check_dict[m]
        return _check_dict

    def get_words(self, user_id: int):
        return [u.word for u in self.users if u.user_id == user_id]


async def Admin(bot: Bot, event: GroupMessageEvent):
    user = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
    return user["role"] in ["owner", "admin"]


@box.on_cmd(cmds=["开放文字市场", "刷新文字市场"])
async def open_word_market(bot: Bot, event: GroupMessageEvent):
    '''刷新文字市场，开放福袋购买'''
    if not await Admin(bot, event):
        await box.send("请联系管理员开放市场，您没有权限")
        return

    market = box.get_data(GroupMarket)
    market.refresh(box.group_id)
    await box.send(f"市场已开放，持续{config.word_tax.open_duration}s，本轮文字池为 {market.words}")


@box.on_cmd(cmds="购买文字")
async def buy_words():
    '''花费金钱购买一次福袋，获得3个随机文字'''
    market = box.get_data(GroupMarket)
    if not market.is_open():
        await box.send("市场未开放，请联系管理员开放市场后再购买")
    else:
        money = get_money(box.group_id, box.user_id)
        money.value -= config.word_tax.buy_price
        words = market.buy(box.group_id, box.user_id, box.user_name)
        await box.send(f"[{box.user_name}] 花费{config.word_tax.buy_price}金，购买了文字 {words}")


@box.on_cmd(cmds="我的文字")
async def buy_words():
    '''查看自己的文字'''
    market = box.get_data(GroupMarket)
    await box.send(f"[{box.user_name}]当前拥有 {market.get_words(box.user_id)}")


@box.on_cmd(cmds="所有文字")
async def buy_words():
    '''查看所有人的文字'''
    market = box.get_data(GroupMarket)
    if market.is_valid():
        items = [f"[{u.uname}] {u.word}" for u in market.users]
        await box.send_many(items)
    else:
        await box.send("这一轮文字税尚未开始")


@box.on_text()
async def get_tax():
    '''计算税收'''
    market = box.get_data(GroupMarket)
    if market.is_open():
        return

    if not market.is_valid():
        return

    msg = box.arg.extract_plain_text()
    check_dict = market.check(msg, box.user_id)
    if not check_dict:
        return

    user_moneys: dict[int, Money] = {}
    for users in check_dict.values():
        for u in users:
            if u.user_id not in user_moneys:
                user_moneys[u.user_id] = get_money(u.group_id, u.user_id)
    user_moneys[box.user_id] = get_money(box.group_id, box.user_id)

    for w in check_dict.keys():
        msg = msg.replace(w, f"[{w}]")
    infos = [msg]

    for w, users in check_dict.items():
        t = int(config.word_tax.tax / len(users))
        tt = t*len(users)
        user_moneys[box.user_id].value -= tt
        for u in users:
            user_moneys[u.user_id].value += t
        names = [u.uname for u in users]
        infos.append(f"[{w}] 所有者：{names}，您为此字付费{tt}金")

    if config.word_tax.tax_notice:
        await box.send_many(infos)
