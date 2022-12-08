'''
    接龙，多个词库可选择
'''
import re
from typing import Dict, List
from pydantic import Field
from pypinyin import lazy_pinyin
from ayaka import AyakaApp, AyakaInput, AyakaLargeConfig, AyakaDB, AyakaConfig
from .dragon import Dragon
from .default_data import default_dragons
from ..bag import UserMoney

app = AyakaApp("接龙")
app.help = '''接龙，在聊天时静默运行'''


class UseInput(AyakaInput):
    name: str = Field(description="词库名称")


class AutoInput(AyakaInput):
    name: str = Field(description="词库名称")
    start: str = Field(description="开头词")
    max_len: int = Field(10, description="最大接龙长度", gt=0)


class DragonUserTable(AyakaDB):
    __table_name__ = "dragon_user_data"
    group_id: int = Field(extra=AyakaDB.__primary_key__)
    user_id: int = Field(extra=AyakaDB.__primary_key__)
    dragon_name: str = Field(extra=AyakaDB.__primary_key__)
    cnt: int = 0

    @classmethod
    def get(cls, dragon: Dragon):
        return cls.select_one(
            dragon_name=dragon.name,
            group_id=app.group_id,
            user_id=app.user_id
        )


DragonUserTable.create_table()


class DragonConfigTable(AyakaDB):
    __table_name__ = "dragon_config"
    group_id: int = Field(extra=AyakaDB.__primary_key__)
    dragon_name: str = Field(extra=AyakaDB.__primary_key__)
    last: str = ""
    use: bool = True

    @classmethod
    def get(cls, dragon: Dragon):
        return cls.select_one(
            dragon_name=dragon.name,
            group_id=app.group_id
        )


DragonConfigTable.create_table()


class DragonData(AyakaLargeConfig):
    __app_name__ = app.name
    dragon_list: List[Dragon] = default_dragons


class Config(AyakaConfig):
    __app_name__ = app.name
    reward: int = 1000


config = Config()

dragon_data = DragonData()


zh = re.compile(r"[\u4e00-\u9fff]+")


@app.on.text()
@app.on_state(app.get_state(), app.root_state)
async def handle(usermoney: UserMoney):
    text = app.event.get_plaintext()
    r = zh.search(text)
    if not r:
        return

    word = r.group()
    name = app.user_name
    for dragon in dragon_data.dragon_list:
        dragon_config = DragonConfigTable.get(dragon)

        if not dragon_config.use:
            continue

        if not dragon.check(word):
            continue

        # 上次接龙
        last = dragon_config.last
        if last and word:
            p1 = lazy_pinyin(last)[-1]
            p2 = lazy_pinyin(word)[0]
            if p1 == p2:
                usermoney.change(config.reward)
                await app.send(f"[{name}] 接龙成功！奖励{config.reward}金")

                # 记录
                user_data = DragonUserTable.get(dragon)
                user_data.cnt += 1
                user_data.save()

        word = dragon.next(word)
        if word:
            await app.send(word)
            dragon_config.last = word
            dragon_config.save()
        else:
            await app.send("%$#*-_")
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
    items = ["所有词库："]
    for dragon in dragon_data.dragon_list:
        dragon_config = DragonConfigTable.get(dragon)
        if dragon_config.use:
            items.append(f"[{dragon.name}] 正在使用")
        else:
            items.append(f"[{dragon.name}]")
    await app.send("\n".join(items))


@app.on.state()
@app.on.command("use")
async def use_dragon(data: UseInput):
    '''使用指定词库'''
    name = data.name
    for dragon in dragon_data.dragon_list:
        if dragon.name == name:
            break
    else:
        await app.send(f"没有找到词库[{name}]")
        return

    dragon_config = DragonConfigTable.get(dragon)
    dragon_config.use = True
    dragon_config.save()
    await app.send(f"已使用[{name}]")


@app.on.state()
@app.on.command("unuse")
async def unuse_dragon(data: UseInput):
    '''关闭指定词库'''
    name = data.name

    for dragon in dragon_data.dragon_list:
        if dragon.name == name:
            break
    else:
        await app.send(f"没有找到词库[{name}]")
        return

    dragon_config = DragonConfigTable.get(dragon)
    dragon_config.use = False
    dragon_config.save()
    await app.send(f"已停用[{name}]")


@app.on.state()
@app.on.command("data")
async def show_data():
    '''展示你的答题数据'''
    data = {}

    user_datas = DragonUserTable.select_many(
        group_id=app.group_id, user_id=app.user_id)
    for dragon in dragon_data.dragon_list:
        for user_data in user_datas:
            if user_data.dragon_name == dragon.name:
                data[dragon.name] = user_data.cnt
                break

    if data:
        info = f"[{app.user_name}]\n"
        for name, cnt in data.items():
            info += f"[{name}] 接龙次数 {cnt}\n"
    else:
        info = "你还没有用过我...T_T"
    await app.send(info.strip())


@app.on.state()
@app.on.command("rank")
async def show_rank():
    '''展示排行榜'''
    data: Dict[str, List[DragonUserTable]] = {}

    user_datas = DragonUserTable.select_many(group_id=app.group_id)
    for user_data in user_datas:
        if user_data.dragon_name not in data:
            data[user_data.dragon_name] = []
        data[user_data.dragon_name].append(user_data)

    # 无人使用
    for dragon in dragon_data.dragon_list:
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
    name = data.name
    word = data.start
    max_len = data.max_len

    for dragon in dragon_data.dragon_list:
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
