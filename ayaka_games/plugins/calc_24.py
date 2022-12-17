'''
    注意，本插件使用了eval ！！！
  
    尽管已有所限制，但不保证代码已排除了所有注入风险！！
'''

import ast
import json
import re
from typing import List, Dict
from random import choice
from pydantic import Field
from ayaka import AyakaApp, AyakaCache, AyakaLargeConfig
from ayaka.extension import singleton, run_in_startup
from .bag import UserMoneyData
from .data.utils import get_path


def get_data_24():
    path = get_path("calc_24", "24.json")
    with path.open("r", encoding="utf8") as f:
        data_24 = json.load(f)
    return data_24


def get_data_48():
    path = get_path("calc_24", "48.json")
    with path.open("r", encoding="utf8") as f:
        data_48 = json.load(f)
    return data_48


@run_in_startup
@singleton
class Config(AyakaLargeConfig):
    __app_name__ = "24点"
    reward: int = 1000
    data_24: Dict[str, dict] = Field(default_factory=get_data_24)
    data_48: Dict[str, dict] = Field(default_factory=get_data_48)


class Question(AyakaCache):
    nums: List[int] = []
    solution: dict = {}


def register(app: AyakaApp, n: int):
    if n == 24:
        def get_data():
            return Config().data_24
    else:
        def get_data():
            return Config().data_48

    def get_questions():
        data = get_data()
        return list(data.keys())

    @app.on_start_cmds(f"{n}点")
    async def _(cache: Question):
        '''启动游戏'''
        await app.start()
        await app.send(app.help)
        await set_q(cache)

    app.set_start_cmds("退出", "exit", "quit")

    @app.on_state()
    @app.on_cmd("出题", "下一题", "next")
    async def set_q(cache: Question):
        q = choice(get_questions())
        nums = q.split(" ")
        solution = get_data()[q]
        cache.nums = [int(n) for n in nums]
        cache.solution = solution
        await app.send(f"{q}\n\nTIPS：本题至少有{len(solution)}种答案（使用不同的运算符）")

    @app.on_state()
    @app.on_cmd("题目", "查看题目", "查看当前题目", "当前题目", "question")
    async def _(cache: Question):
        nums = cache.nums
        solution = cache.solution
        q = " ".join(str(n) for n in nums)
        await app.send(f"{q}\n\nTIPS：本题至少有{len(solution)}种答案（使用不同的运算符）")

    @app.on_state()
    @app.on_cmd("答案", "answer")
    async def _(cache: Question):
        nums = cache.nums
        solution = cache.solution

        if not nums:
            await app.send("请先出题")
            return

        info = "\n".join(solution.values())
        await app.send(info)
        await set_q(cache)

    @app.on_state()
    @app.on_text()
    async def _(cache: Question):
        '''请使用正确的表达式，例如 (1+2)*(3+3)'''
        nums = cache.nums
        if not nums:
            return

        try:
            exp = app.event.get_plaintext()
            exp, r = deal(exp, nums)
        except Exception as e:
            code, info = e.args
            await app.send(info)
            return

        r = "正确！" if abs(r-n) < 0.1 else "错误"
        await app.send(exp + "\n" + r)
        if abs(r-n) < 0.1:
            reward = Config().reward
            UserMoneyData.get(app.user_id).change(reward)
            await app.send(f"奖励{reward}金")


def pre_check(exp: str, nums: list):
    '''初步检查表达式是否合法，且只许使用限定的操作符和数字'''
    # 移除空格，纠正操作符
    exp = exp.strip().replace("\\", "/").replace(" ", "")
    exp = re.sub(r"[（{【\[]", "(", exp)
    exp = re.sub(r"[）}】\]]", ")", exp)

    # 过长的表达式，明显有问题
    if len(exp) > 20:
        raise Exception(-1, "可疑的输入")

    # 解析格式
    try:
        ast.parse(exp)
    except SyntaxError:
        raise Exception(-2, "错误的表达式")

    # 复制一份
    __nums = [n for n in nums]

    # 判断数字是否非法
    _nums = re.findall(r"\d+", exp)
    for num in _nums:
        num = int(num)
        if num not in nums:
            raise Exception(-3, "没有使用给定的数字")
        if num not in __nums:
            raise Exception(-4, "给定数字必须全部使用，且仅可用一次")
        __nums.remove(num)

    if __nums:
        raise Exception(-4, "给定数字必须全部使用，且仅可用一次")

    # 将表达式转为中缀参数数组
    pt1 = re.compile(r"^\d+")
    pt2 = re.compile(r"^([\+\-/\(\)\^]|\*{1,2})")

    args = []
    while exp:
        r = pt1.search(exp)
        if r:
            w = r.group()
            exp = exp[len(w):]
            args.append(int(w))
            continue

        r = pt2.search(exp)
        if r:
            w = r.group()
            exp = exp[len(w):]
            args.append(w)
            continue

        raise Exception(-5, "非法操作符")

    # args仍可能有错误
    return args


def mid_to_post(args: list):
    '''中缀转后缀'''
    isp = {"#": 0, "(": 1, "**": 7, "*": 5, "/": 5, "+": 3, "-": 3, ")": 8}
    icp = {"#": 0, "(": 8, "**": 6, "*": 4, "/": 4, "+": 2, "-": 2, ")": 1}

    args.append("#")
    stack = ["#"]
    rs = []
    for arg in args:
        if isinstance(arg, int):
            rs.append(arg)
            continue

        while stack:
            if isp[stack[-1]] > icp[arg]:
                rs.append(stack.pop())
            elif isp[stack[-1]] == icp[arg]:
                stack.pop()
            else:
                break

        if arg not in [")", "#"]:
            stack.append(arg)

    return rs


def post_check(args: list):
    '''检查后缀参数是否正确'''
    cnt = 0
    for arg in args:
        if isinstance(arg, int):
            cnt += 1
        else:
            cnt -= 1
        if cnt < 1:
            raise Exception(-2, "错误的表达式")


def safe_calc(args: list) -> float:
    '''安全计算后缀表达式，阻断大指数运算'''
    stack = []
    for arg in args:
        if isinstance(arg, int):
            stack.append(arg)
        else:
            b = stack.pop()
            a = stack.pop()

            if arg == "/" and b == 0:
                raise Exception(-2, "错误的表达式")

            if arg == "**" and (a > 1000 or b > 10 or b < 0 or a != int(a) or b != int(b)):
                raise Exception(-6, "恶意表达式")

            c = eval(f"{a}{arg}{b}")
            if c > 10000 or c < -10000:
                raise Exception(-6, "恶意表达式")

            stack.append(c)

    return stack.pop()


def post_to_mid(args: list) -> str:
    '''后缀转中缀'''
    stack = []
    for arg in args:
        if isinstance(arg, int):
            stack.append(arg)
        else:
            b = stack.pop()
            a = stack.pop()
            c = f"({a}{arg}{b})"
            stack.append(c)

    return stack.pop()[1:-1]


def deal(exp, nums):
    args = pre_check(exp, nums)
    args = mid_to_post(args)
    post_check(args)
    r = safe_calc(args)
    exp = post_to_mid(args) + f" = {r}"
    return exp, r


app_1 = AyakaApp("24点")
app_1.help = "加减乘除次方，5种运算符可用；给出4个1-13范围内的数字，请通过以上运算符算出24点"
register(app_1, 24)

app_2 = AyakaApp("48点")
app_2.help = "加减乘除次方，5种运算符可用；给出4个1-13范围内的数字，请通过以上运算符算出48点"
register(app_2, 48)
