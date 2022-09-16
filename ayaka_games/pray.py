from random import randint
from ayaka import *
from .bag import add_money
from .utils.name import get_name

app = AyakaApp("pray", only_group=True)
app.help = '祈福\n[#pray] 为群里随机一人（除了自己）祈祷随机金币\n概率公式\n 1% +66666\n 8% +6666\n60% +666\n30% +66\n 1% -66666'


def get_diff():
    i = randint(0, 99)
    if i == 0:
        return -66666
    if i <= 30:
        return 66
    if i <= 90:
        return 666
    if i <= 98:
        return 6666
    return 66666


@app.on_command(["pray", "祈祷"])
async def handle():
    nodes = await app.bot.get_group_member_list(group_id=app.event.group_id)

    # 排除自己
    nodes = [node for node in nodes if node['user_id'] != app.event.user_id]

    # 找到受害人
    node = nodes[randint(0, len(nodes)-1)]
    uid = node['user_id']
    name = node['card'] if node['card'] else node['nickname']

    prayer_name = get_name(app.event)

    diff = get_diff()
    money = add_money(diff, app.device, uid)

    ans_list = []
    ans_list.append(f"[{prayer_name}]的祈祷，让[{name}]获得 {diff}金")
    if diff < 0:
        ans_list.append(f"反转了，[{name}]损失 {-diff}金")
    ans_list.append(f"[{name}] 现在持有 {money}金")

    await app.bot.send_group_forward_msg(app.event.group_id, ans_list)
