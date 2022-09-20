import json
import re
from ..utils.file import LocalPath
from ayaka import *

path = LocalPath(__file__).get_json_path("data")


def load():
    with path.open("r", encoding="utf8") as f:
        data: dict = json.load(f)
    return data


def save(data: dict):
    beauty_save(path, data)


def get_template(name: str = "") -> str:
    data = load()
    if name and name in data:
        return True, data[name]
    return False, list(data.keys())


def is_exist(name: str):
    data = load()
    return name in data


def set_template(name: str, template: str):
    data = load()

    # 检查格式
    template = template.replace("：", ":")

    # 未闭合或重复嵌套
    cnt = 0
    for t in template:
        if t == "[":
            cnt += 1
        elif t == "]":
            cnt -= 1
        if cnt not in [0, 1]:
            return False, "标签闭合错误"

    if cnt != 0:
        return False, "标签闭合错误"

    # 检测标签格式
    gs = re.findall(r"\[.*?\]", template)
    for g in gs:
        if not re.match(r"\[\d+\]|\[\d+:.*?\]", g):
            return False, f"{g} 格式错误"

    # 保存
    data[name] = template
    save(data)
    return True, "成功保存"
