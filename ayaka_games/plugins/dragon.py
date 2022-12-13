'''
    接龙，多个词库可选择
'''
import re
from typing import Dict, List
from random import choice
from pydantic import BaseModel, Field
from pypinyin import lazy_pinyin
from ayaka.extension import singleton, run_in_startup, Timer
from ayaka import AyakaApp, AyakaInput, AyakaLargeConfig, AyakaDB
from .bag import UserMoneyData
from .utils import get_path

app = AyakaApp("接龙")
app.help = '''接龙，在聊天时静默运行'''


class UseInput(AyakaInput):
    name: str = Field(description="词库名称")


class AutoInput(AyakaInput):
    name: str = Field(description="词库名称")
    start: str = Field(description="开头词")
    max_len: int = Field(10, description="最大接龙长度", gt=0)


class Dragon(BaseModel):
    '''接龙词库'''
    name: str
    words: List[str]
    pinyin_dict: Dict[str, list] = {}

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
        words: List[str] = self.pinyin_dict.get(p)
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
            group_id=app.group_id,
            user_id=app.user_id
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
            group_id=app.group_id
        )


def get_dragon_list():
    with Timer("创建接龙配置文件"):
        path = get_path("data", "dragon", "成语.txt")
        with path.open("r", encoding="utf8") as f:
            lines = [line.strip() for line in f]
        idiom_words = [line for line in lines if line]

        path = get_path("data", "dragon", "原神.txt")
        with path.open("r", encoding="utf8") as f:
            lines = [line.strip() for line in f]
        genshin_words = [line for line in lines if line]

        return [
            Dragon(name="成语", words=idiom_words),
            Dragon(name="原神", words=genshin_words)
        ]


@run_in_startup
@singleton
class Config(AyakaLargeConfig):
    __app_name__ = app.name
    reward: int = 1000
    dragon_list: List[Dragon] = Field(default_factory=get_dragon_list)


zh = re.compile(r"[\u4e00-\u9fff]+")


@app.on_text()
@app.on_state(app.plugin_state, app.root_state)
async def handle(usermoney: UserMoneyData):
    text = app.event.get_plaintext()
    r = zh.search(text)
    if not r:
        return

    config = Config()

    word = r.group()
    name = app.user_name
    for dragon in config.dragon_list:
        dragon_data = DragonData.get(dragon.name)

        if not dragon_data.use:
            continue

        if not dragon.check(word):
            continue

        # 上次接龙
        last = dragon_data.last
        if last and word:
            p1 = lazy_pinyin(last)[-1]
            p2 = lazy_pinyin(word)[0]
            if p1 == p2:
                usermoney.change(config.reward)
                await app.send(f"[{name}] 接龙成功！奖励{config.reward}金")

                # 记录
                user_data = DragonUserData.get(dragon.name)
                user_data.cnt += 1

        word = dragon.next(word)
        if word:
            await app.send(word)
            dragon_data.last = word
        else:
            await app.send(choice(["%$#*-_", "你赢了", "接不上来..."]))
        break


@app.on.idle()
@app.on.command("接龙")
async def app_entrance():
    '''进入管理面板'''
    await app.start()
    await app.send(app.help)


@app.on.state()
@app.on.command("exit", "退出")
async def app_exit():
    '''退出管理面板'''
    await app.close()


@app.on.state()
@app.on.command("list")
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
    await app.send("\n".join(items))


@app.on.state()
@app.on.command("use")
async def use_dragon(data: UseInput):
    '''使用指定词库'''
    config = Config()
    name = data.name
    for dragon in config.dragon_list:
        if dragon.name == name:
            break
    else:
        await app.send(f"没有找到词库[{name}]")
        return

    dragon_data = DragonData.get(dragon.name)
    dragon_data.use = True
    await app.send(f"已使用[{name}]")


@app.on.state()
@app.on.command("unuse")
async def unuse_dragon(data: UseInput):
    '''关闭指定词库'''
    config = Config()
    name = data.name

    for dragon in config.dragon_list:
        if dragon.name == name:
            break
    else:
        await app.send(f"没有找到词库[{name}]")
        return

    dragon_data = DragonData.get(dragon.name)
    dragon_data.use = False
    await app.send(f"已停用[{name}]")


@app.on_state()
@app.on_cmd("data")
async def show_data():
    '''展示你的答题数据'''
    gid = app.group_id
    uid = app.user_id

    user_datas = DragonUserData.select_many(group_id=gid, user_id=uid)

    if user_datas:
        info = "\n".join(
            f"[{u.dragon_name}] 接龙次数 {u.cnt}"
            for u in user_datas
        )
    else:
        info = "你还没有用过我...T_T"

    await app.send(info)


@app.on.state()
@app.on.command("rank")
async def show_rank():
    '''展示排行榜'''
    config = Config()
    data: Dict[str, List[DragonUserData]] = {}

    user_datas = DragonUserData.select_many(group_id=app.group_id)
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

    users = await app.bot.get_group_member_list(group_id=app.group_id)
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
    await app.send(info.strip())


@app.on.state()
@app.on.command("auto")
async def auto_dragon(data: AutoInput):
    '''使用指定词库和起始点自动接龙n个'''
    config = Config()
    name = data.name
    word = data.start
    max_len = data.max_len

    for dragon in config.dragon_list:
        if dragon.name == name:
            break
    else:
        await app.send(f"没有找到词库[{name}]")
        return

    info = word
    for i in range(max_len):
        word = dragon.next(word)
        if word:
            info += " " + word
        else:
            info += info[-1]*3 + "%.$#*-_ 接不动了喵o_O"
            break

    await app.send(info)
