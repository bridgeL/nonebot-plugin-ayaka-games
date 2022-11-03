'''
    接龙，多个词库可选择
'''
import re
from random import choice
from typing import Dict, List, Tuple
from pypinyin import lazy_pinyin
from ayaka import AyakaApp
from ..bag import change_money

app = AyakaApp("接龙")
app.help = '''接龙，在聊天时静默运行'''


def ensure_key_is_int(data: dict):
    data = {int(k): v for k, v in data.items()}
    return data


class UserManager:
    def get_file(self):
        return app.storage.group().jsonfile("user", {})

    def load(self):
        data = self.get_file().load()
        return ensure_key_is_int(data)

    def get_all(self):
        return self.load()

    def get_user(self, uid: int):
        data = self.load()
        return data.get(uid, {})

    def get_cnt(self, name: str, uid: int):
        data = self.load()
        return data.get(uid, {}).get(name, 0)

    def add_cnt(self, name: str, uid: int):
        file = self.get_file()
        data = file.load()
        data = ensure_key_is_int(data)
        user = data.get(uid, {})
        cnt = user.get(name, 0) + 1
        user[name] = cnt
        data[uid] = user
        file.save(data)


user_manager = UserManager()


class Dragon:
    zh = re.compile(r"[\u4e00-\u9fff]+")

    @property
    def use(self):
        return self._use

    @use.setter
    def use(self, val: bool):
        file = app.storage.plugin().jsonfile("use", {})
        data = file.load()
        data[self.name] = val
        file.save(data)

    def __init__(self, name: str) -> None:
        '''加载选择的词库'''
        self.name = name
        self._use = app.storage.plugin().jsonfile("use", {}).load().get(name, True)

        words = app.storage.plugin("词库").file(f"{name}.txt").load().split()
        words = [w for w in words if w]
        search_dict = {}
        for word in words:
            p = lazy_pinyin(word)[0]
            if p not in search_dict:
                search_dict[p] = []
            search_dict[p].append(word)

        self.words = words
        self.search_dict = search_dict

        self.last_p = ""

    def _get_next(self, p: str):
        '''输入拼音返回接龙'''
        # 词穷了
        if p not in self.search_dict:
            return

        # 成功接龙
        next = choice(self.search_dict[p])
        return next

    def get_next(self, text: str) -> Tuple[bool, bool, str]:
        '''
            返回：
            - belong_to_words 是否在词库里
            - last_success 是否成功接了上次的龙
            - next 下一条接龙
        '''
        belong_to_words = False
        last_success = False
        next = ""

        # 提取中文
        word = ""
        r = self.zh.search(text)
        if r:
            word = r.group()

        # 没有中文
        # 不是词库词汇
        if not word or word not in self.words:
            return belong_to_words, last_success, next

        belong_to_words = True

        # 判断是否接了上次的龙
        if self.last_p:
            p = lazy_pinyin(word)[0]
            if p == self.last_p:
                last_success = True

        # 尝试接龙
        p = lazy_pinyin(word)[-1]
        next = self._get_next(p)

        # 词穷了
        if not next:
            # 本次接龙结束
            self.last_p = ""

        # 成功接龙
        else:
            # 更新龙尾
            self.last_p = lazy_pinyin(next)[-1]

        return belong_to_words, last_success, next


dragons: List[Dragon] = []

for p in app.storage.plugin("词库").iterdir():
    dragons.append(Dragon(p.stem))


@app.on.idle()
@app.on.text()
async def handle():
    # 处理
    text = app.event.get_plaintext()
    for dragon in dragons:
        if not dragon.use:
            continue

        belong_to_words, last_success, next = dragon.get_next(text)
        if not belong_to_words:
            continue

        if last_success:
            change_money(app.user_id, 1000)
            await app.send(f"[{app.user_name}] 接龙成功！奖励1000金")

            # 记录
            user_manager.add_cnt(dragon.name, app.user_id)

        if next:
            await app.send(next)
        else:
            await app.send("wo bu hui le")
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
    info = "所有词库：\n"
    for dragon in dragons:
        using = "正在使用" if dragon.use else ""
        info += f"[{dragon.name}] {using}\n"
    await app.send(info)


@app.on.state()
@app.on.command("use")
async def use_dragon():
    '''<词库名称> 使用指定词库'''
    try:
        name = str(app.args[0])
    except:
        await app.send("参数缺失")
        return

    for dragon in dragons:
        if dragon.name == name:
            dragon.use = True
            await app.send(f"已使用[{name}]")
            return

    await app.send(f"没有找到词库[{name}]")


@app.on.state()
@app.on.command("unuse")
async def unuse_dragon():
    '''<词库名称> 关闭指定词库'''
    try:
        name = str(app.args[0])
    except:
        await app.send("参数缺失")
        return

    for dragon in dragons:
        if dragon.name == name:
            dragon.use = False
            await app.send(f"已停用[{name}]")
            return

    await app.send(f"没有找到词库[{name}]")


@app.on.state()
@app.on.command("data")
async def show_data():
    '''展示你的答题数据'''
    userdata: dict = user_manager.get_user(app.user_id)
    if not userdata:
        await app.send("数据为空，还请多多使用本功能")
        return

    info = f"[{app.user_name}]\n"
    for name, cnt in userdata.items():
        info += f"[{name}] 接龙次数 {cnt}\n"
    await app.send(info.strip())


@app.on.state()
@app.on.command("rank")
async def show_rank():
    '''展示排行榜'''
    total: Dict[str, list] = {}
    data = user_manager.get_all()
    for uid, value in data.items():
        for name, cnt in value.items():
            if name not in total:
                total[name] = []
            total[name].append({"uid": uid, "cnt": cnt})

    if not total:
        await app.send("数据为空，还请多多使用本功能")
        return

    users = await app.bot.get_group_member_list(group_id=app.group_id)
    users = {u["user_id"]: u["card"] or u["nickname"] for u in users}

    info = "排行榜\n"
    for name, items in total.items():
        info += f"\n[{name}]\n"
        items.sort(key=lambda x: x["cnt"], reverse=True)
        for item in items:
            uid = item["uid"]
            uname = users[uid]
            cnt = item["cnt"]
            info += f"  - [{uname}] 接龙次数 {cnt}\n"
    await app.send(info.strip())


@app.on.state()
@app.on.command("auto")
async def auto_dragon():
    '''<词库名称> <开头词> 使用指定词库自动接龙10个'''
    try:
        name = str(app.args[0])
        word = str(app.args[1])
        if not word:
            raise
    except:
        await app.send("参数缺失")
        return

    for dragon in dragons:
        if dragon.name == name:
            break
    else:
        await app.send(f"没有找到词库[{name}]")
        return

    info = word
    for i in range(10):
        p = lazy_pinyin(word)[-1]
        next = dragon._get_next(p)
        if next:
            word = next
            info = info + word
        else:
            break

    await app.send(info)
