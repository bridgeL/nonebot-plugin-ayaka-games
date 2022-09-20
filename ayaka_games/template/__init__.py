from collections import defaultdict
import re
from typing import List
from ayaka import *
from .utils import get_template, set_template

app = AyakaApp("模板")
add_help = '''添加方式：[#add/添加 <name> <template>]
template格式：[1]我真的好想你，为了你，我要[2]，[1]，我的[1]，没了你我可怎么活啊[3][3][3]
特殊：你可以为各个参数添加注释，格式为[1:人名]
'''
app.help = {
    "介绍": '''通过模板快速发癫
使用方式：[#mb/模板 <name> <arg1> <arg2> <arg3>]
示例：
#mb 发电1 宝 去裸奔 😭
效果：
宝我真的好想你，为了你，我要去裸奔，宝，我的宝，没了你我可怎么活啊😭😭😭''',
    "run": '[#add/添加 <name> <template>]\n[#list/列表 <name>]',
    "add_name": add_help,
    "add_template": add_help,
}


@app.on_command(["mb", "模板"])
async def app_entrance():
    if not app.args:
        f, info = app.start("run")
        await app.send(info)
        await app.send_help()
        return

    name = app.args[0]
    args = app.args[1:]
    f, template = get_template(name)

    if not f:
        await app.send("模板不存在！")
        return

    # 标签提取
    labels: List[str] = re.findall(r"\[\d+\]|\[\d+:.*?\]", template)
    data = defaultdict(list)
    for label in labels:
        label = label[1:-1]
        if ":" in label:
            num, name = label.split(":", maxsplit=1)
            num = int(num)
        else:
            num = int(label)
            name = ""

        if name not in data[num]:
            data[num].append(name)

    # 标签排序
    items = list(data.items())
    items.sort(key=lambda x: x[0])

    # 数量不足，给出提示
    if len(items) > len(args):
        info = "参数数量不够，该模板的参数有:"

        for num, names in items:
            name = names[0]
            info += "\n" + f"[{num}:{name}]" if name else f"[{num}]"

        info += f"\n你只提供了{len(args)}个"
        await app.send(info)
        return

    # 依次替换
    for i, item in enumerate(items):
        num, names = item
        for name in names:
            label = f"[{num}:{name}]" if name else f"[{num}]"
            template = template.replace(label, args[i])

    await app.send(template)


@app.on_command(["list", "列表"], "run")
async def show():
    if not app.args:
        f, data = get_template()
        data = "现存模板目录如下\n" + "\n".join(f"[{d}]" for d in data)
    else:
        f, data = get_template(app.args[0])
        if not f:
            data = "没找到指定模板，现存模板目录如下\n" + "\n".join(f"[{d}]" for d in data)

    await app.send(data)


@app.on_command(["exit", "退出"], "run")
async def exit_app():
    f, info = app.close()
    await app.send(info)


@app.on_command(["exit", "退出"], ["add_name", "add_template"])
async def exit_add():
    app.state = "run"
    await app.send_help()


@app.on_command(["add", "添加"], "run")
async def add_entrance():
    if not app.args:
        app.state = "add_name"
        await app.send("请输入模板名称")

    elif len(app.args) == 1:
        await add_name(app.args[0])

    else:
        await add_template(app.args[0], app.args[1])


async def add_name(name: str):
    f, _ = get_template(name)
    if f:
        await app.send("[警告] 已存在同名发电模板，再次写入将覆盖")

    app.state = "add_template"
    app.cache.name = name
    await app.send(f"正在添加发电模板[{name}]")
    await app.send("请输入模板内容")


@app.on_text("add_name")
async def add_name_handle():
    await add_name(app.args[0])


async def add_template(name: str, template: str):
    f, info = set_template(name, template)
    if f:
        await app.send(f"已添加发电模板[{name}]\n{template}")
        await exit_add()
        return

    await app.send(info)


@app.on_text("add_template")
async def add_template_handle():
    name = app.cache.name
    await add_template(name, app.args[0])
