'''
    接龙，多个词库可选择
'''
import re
from random import choice
from typing import Dict, List
from pydantic import Field
from pypinyin import lazy_pinyin
from ayaka import AyakaApp, AyakaInputModel
from pathlib import Path
from ..bag import change_money

app = AyakaApp("接龙")
app.help = '''接龙，在聊天时静默运行'''


class UseInput(AyakaInputModel):
    name: str = Field(description="词库名称")


class AutoInput(AyakaInputModel):
    name: str = Field(description="词库名称")
    start: str = Field(description="开头词")
    max_len: int = Field(10, description="最大接龙长度", gt=0)


class Dragon:
    def __init__(self, path: Path) -> None:
        self.name = path.stem
        with path.open("r", encoding="utf8") as f:
            data = f.read()
        words = data.strip().split("\n")
        self.words = [w for w in words if w]

        # 拼音速查表
        self.dict: Dict[str, list] = {}
        for word in self.words:
            # 获取首字的拼音
            p = lazy_pinyin(word)[0]
            if p not in self.dict:
                self.dict[p] = []
            self.dict[p].append(word)

    def check(self, word: str):
        return word in self.words

    def next(self, word: str):
        # 获取末字的拼音
        p = lazy_pinyin(word)[-1]
        words: List[str] = self.dict.get(p)
        if not words:
            return ""
        return choice(words)


dragon_list: List[Dragon] = []

wordsbin_path = app.storage.plugin_path("词库")
for path in wordsbin_path.iterdir():
    dragon_list.append(Dragon(path))


zh = re.compile(r"[\u4e00-\u9fff]+")


@app.on.idle()
@app.on.text()
async def handle():
    text = app.event.get_plaintext()
    r = zh.search(text)
    if not r:
        return

    word = r.group()
    uid = app.user_id
    name = app.user_name
    use_file = app.storage.group_path().json("use")
    cnt_file = app.storage.group_path().json("cnt")
    for dragon in dragon_list:
        use_ctrl = use_file.chain(dragon.name)
        cnt_ctrl = cnt_file.chain(dragon.name, uid)
        last_ctrl = app.cache.chain(dragon.name, "last")

        use = use_ctrl.get(True)
        if not use:
            continue

        if not dragon.check(word):
            continue

        last = last_ctrl.get("")
        if last and word:
            p1 = lazy_pinyin(last)[-1]
            p2 = lazy_pinyin(word)[0]
            if p1 == p2:
                change_money(uid, 1000)
                await app.send(f"[{name}] 接龙成功！奖励1000金")

                # 记录
                cnt_ctrl.set(cnt_ctrl.get(0) + 1)

        word = dragon.next(word)
        if word:
            await app.send(word)
            last_ctrl.set(word)
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
    use_file = app.storage.group_path().json("use")
    items = ["所有词库："]
    for dragon in dragon_list:
        use = use_file.chain(dragon.name).get(True)
        if use:
            items.append(f"[{dragon.name}] 正在使用")
        else:
            items.append(f"[{dragon.name}]")
    await app.send("\n".join(items))


@app.on.state()
@app.on.command("use")
@app.on_model(UseInput)
async def _use_dragon():
    '''使用指定词库'''
    data: UseInput = app.model_data
    name = data.name

    for dragon in dragon_list:
        if dragon.name == name:
            break
    else:
        await app.send(f"没有找到词库[{name}]")
        return

    use_file = app.storage.group_path().json("use")
    use_ctrl = use_file.chain(name)
    use_ctrl.set(True)
    await app.send(f"已使用[{name}]")


@app.on.state()
@app.on.command("unuse")
@app.on_model(UseInput)
async def _unuse_dragon():
    '''关闭指定词库'''
    data: UseInput = app.model_data
    name = data.name

    for dragon in dragon_list:
        if dragon.name == name:
            break
    else:
        await app.send(f"没有找到词库[{name}]")
        return

    use_file = app.storage.group_path().json("use")
    use_ctrl = use_file.chain(name)
    use_ctrl.set(False)
    await app.send(f"已停用[{name}]")


@app.on.state()
@app.on.command("data")
async def show_data():
    '''展示你的答题数据'''
    uid = app.user_id
    data = {}
    cnt_file = app.storage.group_path().json("cnt")
    for dragon in dragon_list:
        cnt_ctrl = cnt_file.chain(dragon.name, uid)
        data[dragon.name] = cnt_ctrl.get(0)

    info = f"[{app.user_name}]\n"
    for name, cnt in data.items():
        info += f"[{name}] 接龙次数 {cnt}\n"
    await app.send(info.strip())


@app.on.state()
@app.on.command("rank")
async def show_rank():
    '''展示排行榜'''
    cnt_file = app.storage.group_path().json("cnt")
    cnt_ctrl = cnt_file.chain()
    if not cnt_ctrl.get():
        await app.send("数据为空，还请多多使用本功能")
        return

    users = await app.bot.get_group_member_list(group_id=app.group_id)
    users = {u["user_id"]: u["card"] or u["nickname"] for u in users}

    info = "排行榜\n"
    for dragon in dragon_list:
        info += f"\n[{dragon.name}]\n"
        data: dict = cnt_ctrl.chain(dragon.name).get({})
        print(data)
        items = list(data.items())
        items.sort(key=lambda x: x[1], reverse=True)
        for uid, cnt in items:
            info += f"  - [{users[int(uid)]}] 接龙次数 {cnt}\n"
    await app.send(info.strip())


@app.on.state()
@app.on.command("auto")
@app.on_model(AutoInput)
async def auto_dragon():
    '''使用指定词库和起始点自动接龙n个'''
    data: AutoInput = app.model_data
    name = data.name
    word = data.start
    max_len = data.max_len

    for dragon in dragon_list:
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
