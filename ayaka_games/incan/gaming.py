from .model import Incan, Card, choice, Deck
from .app import app
from .quit import exit_incan

warnings = [
    '人类，离开此地！',
    '吾等奉命守护此地，驱逐一切外来者',
    '别让我第二次看到你'
]

findArtifact = [
    '就是这个！谢谢你帮我找到它！能将这孩子带出神殿么？', '这是……我留下的……遗物？',
    '虽说是我最重要的东西，但埋藏在神殿里的话根本就没意义嘛！',
    '遗物流通于世，这个世界一定会发生某些变化吧~真是期待呢~',
    '遗物拥有特殊的力量，沉睡在神殿里的话是没办法苏醒的呢~'
]

goddess = [
    '有且仅有一个人撤退才能带走遗物哦~趁别人不知道的时候偷偷撤退吧！',
    '说起来，我曾在神殿一共制造了5个魔偶呢~欸？难道说已经见过了？危险了啊，赶快离开比较好哦！'
    '帮我带出遗物的话，宝石什么的，要多少有多少哦~'
    '不能平分的东西为什么不能被带走呢？啊，难道是因为自己得不到的东西也不能让别人得到？'
    '沿原路返回的时候可以拿到来时没能平分的宝石和遗物哦~',
    '<Turquoise>有1积分，<Obsidian>有5积分，<Gold>竟然有10积分吗！？'
    '遗物只要出现了一次就不会再出现了呢~'
    '就算发生的概率再低，对于面对的人来说，概率就是100%呢'
    '只要尺度足够大，一切事件都必然发生，那么，谁是幸运儿呢？'
    '幸运或者不幸，对我来说都没有意义，那是从人类的角度才存在的东西'
]

deads = [
    '下次不要这么贪了哦~'
    '多亏了你们，我重新获得了这只魔偶的控制权呢，你们不会再遇到这孩子了',
    '该说是有勇气呢还是无谋呢还是说盲目自信呢……不是很懂你们这些人类。'
    '不要放弃，下次更加谨慎一点吧！'
]


async def EnterNextRound(model: Incan):
    model.turn = 0
    model.monsters.clear()
    model.route.clear()
    for i in range(model.artifact):
        model.deck.DrawArtifact()

    for uid in model.members:
        model.members[uid]['status'] = 0
        for name in model.members[uid]['treasures']:
            model.members[uid]['income'][name]['number'] += model.members[uid]['treasures'][name]['number']
            model.members[uid]['treasures'][name]['number'] = 0

    model.round += 1
    if model.round == 5:
        return await Clearing(model)
    else:
        await app.send(f'第{model.round}轮结束')
        await app.send(f'第{model.round+1}轮：{model.temples.Draw().name}')


async def Clearing(model: Incan):
    alternate_uid = []
    alternate_value = 0

    for uid, member in model.members.items():
        income = 0
        for name, jewel in member['income'].items():
            income += jewel['number'] * jewel['value']
        if income > alternate_value:
            alternate_uid.clear()
            alternate_uid.append(uid)
            alternate_value = income
        elif income == alternate_value and income > 0:
            alternate_uid.append(uid)

    if alternate_value > 0:
        relic = -1
        winner = []
        for uid in alternate_uid:
            if model.members[uid]['income']['Artifact']['number'] > relic:
                relic = model.members[uid]['income']['Artifact']['number'] > relic
                winner.clear()
                winner.append(uid)
            elif relic == model.members[uid]['income']['Artifact']['number'] and relic > 0:
                winner.append(uid)

        for uid in winner:
            trophy = []
            for name, jewel in model.members[uid]['income'].items():
                trophy.append(f'<{name}>{jewel["number"]}枚')
            await app.send(f'<{model.members[uid]["name"]}>带着{", ".join(trophy)}获得了胜利')
            await app.send('游戏结束~')

    else:
        await app.send('有勇气才能获得宝石哦！')
        await app.send('游戏结束~')

    return True


async def DoRetreat(model: Incan):
    runaways = [
        uid for uid in model.members if model.members[uid]['status'] == 2]
    num = len(runaways)
    if num == 0:
        return

    for card in model.route:
        for uid in runaways:
            model.members[uid]['treasures'][card.name]['number'] += card.number // num
        if card.ctype is Card.Type.ARTIFACT and num == 1:
            model.acquiredArtifact += 1
            if model.acquiredArtifact > 2:
                model.members[uid]['treasures'][card.name]['value'] = 10
        card.number = card.number % num

    names = ",".join(f'<{model.members[uid]["name"]}>' for uid in runaways)
    await app.send(f'{names}放弃了冒险')


async def send_info(turn, result, tips_giver, tips):
    await app.send(f'第{turn}回合, {result}\n<{tips_giver}> {tips}')


async def Gaming(model: Incan):
    # CheckTurnEnd
    for uid in model.members:
        if model.members[uid]['status'] == 0:
            return

    model.turn += 1
    await DoRetreat(model)
    for uid in model.members:
        if model.members[uid]['status'] == 1:
            model.members[uid]['status'] = 0
        elif model.members[uid]['status'] == 2:
            model.members[uid]['status'] = 3

    adventures = [
        uid for uid in model.members if model.members[uid]['status'] == 0]

    if adventures:
        card = None
        if model.turn == 1:
            card = model.deck.DrawJewel()
        else:
            card = model.deck.Draw()
        if card.ctype is Card.Type.MONSTER:
            if card.name in model.monsters:
                for uid in adventures:
                    for jewel in model.members[uid]['treasures'].values():
                        jewel['number'] = 0

                names = ",".join(
                    f'<{model.members[uid]["name"]}>' for uid in adventures)
                await send_info(model.turn, f"{names}被<{card.name}>驱逐出神殿，一无所获", "概率女神", choice(deads))

                model.deck = Deck()
                model.deck.Remove(card.name)
                return await EnterNextRound(model)
            else:
                model.monsters.append(card.name)
                await send_info(model.turn, f"发现了来自<{card.name}>的警告", card.name, choice(warnings))
        elif card.ctype is Card.Type.JEWEL:
            await send_info(model.turn, f"发现了宝石<{card.name}>{card.number}枚", "概率女神", choice(goddess))
            num = len(adventures)
            for uid in adventures:
                model.members[uid]['treasures'][card.name]['number'] += card.number // num
            card.number = card.number % num
            model.route.append(card)
        elif card.ctype is Card.Type.ARTIFACT:
            model.route.append(card)
            model.artifact += 1
            await send_info(model.turn, f"发现了遗物<{card.name}>", "概率女神", choice(findArtifact))
    else:
        model.deck = Deck()
        return await EnterNextRound(model)


@app.on_command(['go', 'forward'], "gaming")
async def handle():
    model: Incan = app.cache.model
    uid = app.event.user_id
    if model.members[uid]['status'] == 0:
        model.members[uid]['status'] = 1
    if await Gaming(model):
        await exit_incan(app, model)


@app.on_command(['back', 'retreat', 'escape'], "gaming")
async def handle():
    model: Incan = app.cache.model
    uid = app.event.user_id
    if model.members[uid]['status'] == 0:
        model.members[uid]['status'] = 2
    if await Gaming(model):
        await exit_incan(app, model)
