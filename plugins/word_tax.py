from random import sample
from time import time
from ayaka import AyakaBox, AyakaUserDB, AyakaDB, AyakaConfig, BaseModel, Bot, GroupMessageEvent, Field, slow_load_config
from .bag import get_money

box = AyakaBox("文字税")


@slow_load_config
class Config(AyakaConfig):
    __config_name__ = box.name
    words: str = ""
    tax: int = 100


class UserWord(AyakaUserDB):
    __table_name__ = "user_word"
    words: str = ""
    time: int = 0


class Word(AyakaDB):
    __table_name__ = "group_word"
    group_id: int = Field(extra=AyakaDB.__primary_key__)
    word: str = Field(extra=AyakaDB.__primary_key__)
    cnt: int = 0
    time: int = 0
    owners: list = Field([], extra=AyakaDB.__json_key__)


class Market(BaseModel):
    open_time: int = 0
    words: str = ""

    def refresh(self, group_id):
        config = Config()
        self.open_time = int(time())
        self.words = "".join(sample(config.words, 20))
        _words = [
            Word.select_one(group_id=group_id, word=w)
            for w in self.words
        ]
        for w in _words:
            w.cnt = 0
            w.time = self.open_time
            w.owners = []

    def is_open(self):
        return int(time()) - self.open_time <= 600

    def buy(self, group_id):
        words = "".join(sample(self.words), 3)
        _words = [
            Word.select_one(group_id=group_id, word=w)
            for w in words
        ]
        for w in _words:
            w.owners.append()
        return words


async def Admin(bot: Bot, event: GroupMessageEvent):
    user = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
    return user["role"] in ["owner", "admin"]


@box.on_cmd(cmds=["开放文字市场", "刷新文字市场"])
async def open_word_market(bot: Bot, event: GroupMessageEvent):
    '''刷新文字市场，开放福袋购买十分钟'''
    if not Admin(bot, event):
        await box.send("请联系管理员开放市场，您没有权限")
        return

    market = box.get_data(Market)
    market.refresh()
    await box.send(f"市场已开放，持续十分钟，本轮文字池为 {market.words}")


@box.on_cmd(cmds=["购买文字"])
async def buy_words():
    '''花费1000金购买一次福袋，随机获得3个文字'''
    market = box.get_data(Market)
    if not market.is_open():
        await box.send("市场未开放，请联系管理员开放市场后再购买")
    else:
        money = get_money(box.group_id, box.user_id)
        money.value -= 1000
        user_word = Word.select_one(
            group_id=box.group_id,
            user_id=box.user_id,
        )
        words = market.buy()
        user_word.words = words
        user_word.time = int(time())
        await box.send(f"[{box.user_name}] 花费1000金，购买了文字 {words}")


# @box.on_text()
# async def get_tax():
#     '''计算税收'''
#     market = box.get_data(Market)
#     if not market.is_open():
#         await box.send("市场未开放，请联系管理员开放市场后再购买")
#     else:
#         money = get_money(box.group_id, box.user_id)
#         money.value -= 1000
#         user_word = UserWord.select_one(
#             group_id=box.group_id,
#             user_id=box.user_id,
#         )
#         words = market.buy()
#         user_word.words = words
#         user_word.time  = int(time())
#         await box.send(f"[{box.user_name}] 花费1000金，购买了文字 {words}")
