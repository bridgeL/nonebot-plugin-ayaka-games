from .model import Incan
from .app import app


@app.on_command("status", "inqueue")
async def handle():
    model: Incan = app.cache.model
    ans = f'队伍玩家有：<{">, <".join([model.members[uid]["name"] for uid in model.members])}>'
    await app.send(ans)


@app.on_command("status", "gaming")
async def handle():
    model: Incan = app.cache.model

    status = '角色状态：'
    for uid in model.members:
        state = '还在迷茫中' if model.members[uid]['status'] == 0 else None
        if state is None:
            state = '放弃冒险了' if model.members[uid]['status'] == 3 else '决定好了'
        status += f'<{model.members[uid]["name"]}> {state}\n'
    if model.monsters:
        status += f'警告：\n<{">, <".join(model.monsters)}>'
    else:
        status += f'目前没有收到任何警告'
    
    await app.send(status)
