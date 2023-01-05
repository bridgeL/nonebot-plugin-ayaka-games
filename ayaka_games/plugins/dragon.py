'''
    接龙，多个词库可选择
'''
import re
from random import choice
from pypinyin import lazy_pinyin
from ayaka import AyakaBox, singleton, run_in_startup, Timer, AyakaDB, AyakaConfig, BaseModel, Field
from .bag import get_money
from .data import load_data

box = AyakaBox("接龙")
help = '''接龙，在聊天时静默运行'''


class Dragon(BaseModel):
    '''接龙词库'''
    name: str
    words: list[str]
    pinyin_dict: dict[str, list] = {}

    def __init__(self, **data) -> None:
        super().__init__(**data)

        if not self.pinyin_dict:
            self.get_dict()

    def get_dict(self):
        for word in self.words:
            # 获取首字的拼音
            p = lazy_pinyin(word)[0]
            if p not in self.pinyin_dict:
                self.pinyin_dict[p] = []
            self.pinyin_dict[p].append(word)

    def check(self, word: str):
        return word in self.words

    def next(self, word: str):
        # 获取末字的拼音
        p = lazy_pinyin(word)[-1]
        words: list[str] = self.pinyin_dict.get(p)
        if not words:
            return ""
        return choice(words)


class DragonUserData(AyakaDB):
    '''用户数据'''
    __table_name__ = "dragon_user_data"
    group_id: int = Field(extra=AyakaDB.__primary_key__)
    user_id: int = Field(extra=AyakaDB.__primary_key__)
    dragon_name: str = Field(extra=AyakaDB.__primary_key__)
    cnt: int = 0

    @classmethod
    def get(cls, dragon_name: str):
        return cls.select_one(
            dragon_name=dragon_name,
            group_id=box.group_id,
            user_id=box.user_id
        )


class DragonData(AyakaDB):
    '''词库数据'''
    __table_name__ = "dragon_data"
    group_id: int = Field(extra=AyakaDB.__primary_key__)
    dragon_name: str = Field(extra=AyakaDB.__primary_key__)
    last: str = ""
    use: bool = True

    @classmethod
    def get(cls, dragon_name: str):
        return cls.select_one(
            dragon_name=dragon_name,
            group_id=box.group_id
        )


def get_dragon_list():
    with Timer("创建接龙配置文件"):
        idiom_words = load_data("dragon", "成语.txt")
        genshin_words = load_data("dragon", "原神.txt")
        return [
            Dragon(name="成语", words=idiom_words),
            Dragon(name="原神", words=genshin_words)
        ]


@run_in_startup
@singleton
class Config(AyakaConfig):
    __config_name__ = box.name
    reward: int = 1000
    dragon_list: list[Dragon] = Field(default_factory=get_dragon_list)


zh = re.compile(r"[\u4e00-\u9fff]+")


@box.on_text(states=["*", "idle"])
async def handle():
    text = box.event.get_plaintext()
    r = zh.search(text)
    if not r:
        return

    word = r.group()
    config = Config()

    uid = box.user_id
    name = box.user_name
    for dragon in config.dragon_list:
        dragon_data = DragonData.get(dragon.name)

        # 接龙正在使用，且当前词语符合接龙词库
        if dragon_data.use and dragon.check(word):

            # 上次接龙
            last = dragon_data.last

            # 成功接龙
            if last and word:
                p1 = lazy_pinyin(last)[-1]
                p2 = lazy_pinyin(word)[0]
                if p1 == p2:
                    # 修改金钱
                    usermoney = get_money(
                        group_id=box.group_id, user_id=box.user_id)
                    usermoney.value += config.reward
                    await box.send(f"[{name}] 接龙成功！奖励{config.reward}金")

                    # 修改记录
                    user_data = DragonUserData.get(dragon.name)
                    user_data.cnt += 1

            # 无论是否成功接龙都发送下一个词
            word = dragon.next(word)
            if word:
                dragon_data.last = word
            else:
                word = choice(["%$#*-_", "你赢了", "接不上来..."])
            await box.send(word)
            break


box.set_start_cmds(cmds="接龙")
box.set_close_cmds(cmds=["exit", "退出"])


@box.on_cmd(cmds=["list"], states=["menu"])
async def list_all():
    '''列出所有词库'''
    config = Config()
    items = ["所有词库："]
    for dragon in config.dragon_list:
        dragon_data = DragonData.get(dragon.name)
        if dragon_data.use:
            items.append(f"[{dragon.name}] 正在使用")
        else:
            items.append(f"[{dragon.name}]")
    await box.send("\n".join(items))


@box.on_cmd(cmds=["use"], states=["menu"])
async def use_dragon():
    '''使用指定词库'''
    config = Config()
    name = str(box.arg)
    for dragon in config.dragon_list:
        if dragon.name == name:
            break
    else:
        await box.send(f"没有找到词库[{name}]")
        return

    dragon_data = DragonData.get(dragon.name)
    dragon_data.use = True
    await box.send(f"已使用[{name}]")


@box.on_cmd(cmds=["unuse"], states=["menu"])
async def unuse_dragon():
    '''关闭指定词库'''
    config = Config()
    name = str(box.arg)

    for dragon in config.dragon_list:
        if dragon.name == name:
            break
    else:
        await box.send(f"没有找到词库[{name}]")
        return

    dragon_data = DragonData.get(dragon.name)
    dragon_data.use = False
    await box.send(f"已停用[{name}]")


@box.on_cmd(cmds=["data"], states=["menu"])
async def show_data():
    '''展示你的答题数据'''
    gid = box.group_id
    uid = box.user_id

    user_datas = DragonUserData.select_many(group_id=gid, user_id=uid)

    if user_datas:
        info = "\n".join(
            f"[{u.dragon_name}] 接龙次数 {u.cnt}"
            for u in user_datas
        )
    else:
        info = "你还没有用过我...T_T"

    await box.send(info)


@box.on_cmd(cmds=["rank"], states=["menu"])
async def show_rank():
    '''展示排行榜'''
    config = Config()
    data: dict[str, list[DragonUserData]] = {}

    # SELECT * from dragon_user_data ORDER BY dragon_name, cnt DESC
    user_datas = DragonUserData.select_many(group_id=box.group_id)
    for user_data in user_datas:
        if user_data.dragon_name not in data:
            data[user_data.dragon_name] = []
        data[user_data.dragon_name].append(user_data)

    # 无人使用
    for dragon in config.dragon_list:
        for user_data in user_datas:
            if user_data.dragon_name == dragon.name:
                break
        else:
            data[dragon.name] = []

    users = await box.bot.get_group_member_list(group_id=box.group_id)
    users = {u["user_id"]: u["card"] or u["nickname"] for u in users}

    info = "排行榜\n"
    for dragon_name, datas in data.items():
        info += f"\n[{dragon_name}]\n"
        if not datas:
            info += f"  - 暂时没人使用过...T_T\n"
        else:
            datas.sort(key=lambda x: x.cnt, reverse=1)
            for d in datas[:5]:
                info += f"  - [{users[d.user_id]}] 接龙次数 {d.cnt}\n"
    await box.send(info.strip())


@box.on_cmd(cmds=["auto"], states=["menu"])
async def auto_dragon():
    '''使用指定词库和起始点自动接龙n个'''
    config = Config()
    name = box.args[0]
    word = box.args[1]
    max_len = box.args[2]

    for dragon in config.dragon_list:
        if dragon.name == name:
            break
    else:
        await box.send(f"没有找到词库[{name}]")
        return

    info = word
    for i in range(max_len):
        word = dragon.next(word)
        if word:
            info += " " + word
        else:
            info += info[-1]*3 + "%.$#*-_ 接不动了喵o_O"
            break

    await box.send(info)
