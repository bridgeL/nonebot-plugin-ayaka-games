from .model import Incan
from .app import app
from ayaka import AyakaApp


async def exit_incan(app: AyakaApp, model: Incan):
    device_id = app.device.device_id
    for uid in model.members:
        dev = await app.abot.get_device(uid)
        if dev:
            await dev.remove_listener(device_id)

    await app.send('游戏结束~下次再见~')

    f, info = app.close()
    await app.send(info)


@app.on_command(['exit', 'quit', "退出"], ["inqueue", "gaming"])
async def handle():
    await exit_incan(app, app.cache.model)
