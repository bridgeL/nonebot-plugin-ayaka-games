from .app import app

app.help = '''指令列表: 
[start/run] 开始游戏
[join] 加入游戏
[status] 查看状态
[go/back] 前进/撤退
[rule/doc] 查看规则
[exit/quit] 退出'''

ruledoc = '''1. 前进，玩家翻开一张卡牌
2. 撤退，玩家沿着来时的路径原路返回
3. 遇到宝石，玩家平分宝石，剩余的宝石留在原地
4. 遇到遗物，当且仅当一名玩家撤退时可从卡片上获得遗物
5. 在前进时遇到怪物，第二次遇到将被驱逐出神殿，丢失此轮在神殿中获得的一切收益
6. 前两个被带出的遗物计5分，后3个被带出的遗物计10分'''

@app.on_command(['rule', 'document', 'doc'], ["inqueue", "gaming"])
async def handle():
    await app.send(ruledoc)
