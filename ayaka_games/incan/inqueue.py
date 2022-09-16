from .model import Incan
from .app import app
from .ready import InitPlayer


@app.on_command(['start', 'run'], "inqueue")
async def handle():
    model: Incan = app.cache.model
    app.state = "gaming"

    await app.send('游戏开始，输入[go/back]决定前进/撤退，此指令支持私聊我发出哦~')
    await app.send(f'第1轮：{model.temples.Draw().name}')

    device_id = app.device.device_id
    for uid in model.members:
        dev = await app.abot.get_device(uid)
        if dev:
            await dev.add_listener(device_id)


@app.on_command("join", "inqueue")
async def handle():
    model: Incan = app.cache.model
    name = app.event.sender.card if app.event.sender.card else app.event.sender.nickname
    uid = app.event.user_id

    if uid in model.members:
        await app.send(f'{name}已经在小队中了，无需重复加入')
    else:
        InitPlayer(model, uid, name)
        await app.send(f'<{name}>加入了小队，当前小队共{len(model.members)}人。')
