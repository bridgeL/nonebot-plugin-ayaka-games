'''
    接龙，多个词库可选择
'''
import json
import re
from random import choice
from typing import Dict, List, Tuple
from pypinyin import lazy_pinyin
from .bag import change_money
from ayaka import AyakaApp

app = AyakaApp("接龙")
app.help = '''接龙，在聊天时静默运行
管理指令：
- 接龙 进入管理面板
- use <词库名称> 使用指定词库
- unuse <词库名称> 关闭指定词库
- list 列出所有词库
- data 展示你的答题数据
- rank 展示排行榜
- exit 退出管理面板
'''


class Dragon:
    zh = re.compile(r"[\u4e00-\u9fff]+")

    @property
    def use(self):
        if self._use.load() == "False":
            return False
        return True

    @use.setter
    def use(self, val: bool):
        self._use.save(val)

    def __init__(self, name: str) -> None:
        '''加载选择的题库'''
        self.name = name
        self._use = app.plugin_storage(name, "use.txt", default="True")

        words = app.plugin_storage(
            name, "bin.txt",
            default=""
        ).load().split()
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

        # 词穷了
        if p not in self.search_dict:
            # 本次接龙结束
            self.last_p = ""
            return belong_to_words, last_success, next

        # 成功接龙
        next = choice(self.search_dict[p])

        # 更新龙尾
        self.last_p = lazy_pinyin(next)[-1]
        return belong_to_words, last_success, next


dragons: List[Dragon] = []

for p in app.plugin_storage().path.iterdir():
    dragons.append(Dragon(p.stem))


@app.on_text()
async def handle():
    # 记录
    file = app.group_storage(f"{app.user_id}.json", default={})
    userdata: dict = file.load()

    # 处理
    text = app.event.get_plaintext()
    for dragon in dragons:
        if not dragon.use:
            continue

        belong_to_words, last_success, next = dragon.get_next(text)
        if not belong_to_words:
            continue

        if last_success:
            change_money(1000, app.user_id)
            await app.send(f"[{app.user_name}] 接龙成功！奖励1000金")

            # 记录
            cnt = userdata.get(dragon.name, 0)
            cnt += 1
            userdata[dragon.name] = cnt

        if next:
            await app.send(next)
        else:
            await app.send("wo bu hui le")
        break

    file.save(userdata)


@app.on_command("接龙")
async def app_entrance():
    await app.start()
    await app.send(app.help)


@app.on_state_command("exit")
async def app_exit():
    await app.close()


@app.on_state_command("list")
async def list_all():
    info = "所有词库：\n"
    for dragon in dragons:
        using = "正在使用" if dragon.use else ""
        info += f"[{dragon.name}] {using}\n"
    await app.send(info)


@app.on_state_command("use")
async def use_dragon():
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


@app.on_state_command("unuse")
async def unuse_dragon():
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


@app.on_state_command("data")
async def show_data():
    userdata: dict = app.group_storage(
        f"{app.user_id}.json", default={}).load()
    if not userdata:
        await app.send("数据为空，还请多多使用本功能")
        return

    info = f"[{app.user_name}]\n"
    for name, cnt in userdata.items():
        info += f"[{name}] 接龙次数 {cnt}\n"
    await app.send(info.strip())


@app.on_state_command("rank")
async def show_rank():
    total: Dict[str, list] = {}
    for p in app.group_storage().path.iterdir():
        uid = p.stem
        with p.open("r", encoding="utf8") as f:
            userdata: dict = json.load(f)
            for name, cnt in userdata.items():
                if name not in total:
                    total[name] = []
                total[name].append({"uid": uid, "cnt": cnt})

    if not total:
        await app.send("数据为空，还请多多使用本功能")
        return

    users = await app.bot.get_group_member_list(group_id=app.group_id)
    users = {str(u["user_id"]): u["card"] or u["nickname"] for u in users}

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
