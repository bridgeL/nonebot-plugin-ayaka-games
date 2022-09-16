from .model import Incan
from .app import app

greeting = '''欢迎使用印加宝藏2.0
输入[join]加入游戏
输入[start/run]开始游戏
输入[help]可以查看指令列表
输入[rule/doc查看游戏规则
如果在游戏过程中有什么问题或建议，请@灯夜(2692327749)'''

treasures = {
    'Turquoise': {
        'number': 0,
        'value': 1
    },
    'Obsidian': {
        'number': 0,
        'value': 5
    },
    'Gold': {
        'number': 0,
        'value': 10
    },
    'Artifact': {
        'number': 0,
        'value': 5
    }
}


def InitPlayer(self: Incan, uid, name):
    from copy import deepcopy
    self.members[uid] = {
        'status': 0,
        'name': name,
        'treasures': treasures,
        'income': deepcopy(treasures)
    }


@app.on_command(["incan", "印加"])
async def game_entrance():
    f, info = app.start("inqueue")
    await app.send(info)

    # 初始化模型
    model = Incan()

    # 缓存
    app.cache.model = model

    name = app.event.sender.card if app.event.sender.card else app.event.sender.nickname
    uid = app.event.user_id

    # 操作
    InitPlayer(model, uid, name)
    await app.send(greeting)
