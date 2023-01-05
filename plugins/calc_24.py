import re
from random import choice
from pydantic import root_validator
from ayaka import AyakaBox, AyakaConfig, BaseModel, Field, logger, slow_load_config
from .bag import get_money
from .data import load_data

PLUGIN_VERSION = "v2"


@slow_load_config
class Config(AyakaConfig):
    __config_name__ = "24点"
    version: str = PLUGIN_VERSION
    reward: int = 1000
    data_24: dict[str, list] = Field(
        default_factory=lambda: load_data("calc_24", "24.json"))
    data_48: dict[str, list] = Field(
        default_factory=lambda: load_data("calc_24", "48.json"))

    @root_validator(pre=True)
    def check_version(cls, values: dict):
        if values.get("version") != PLUGIN_VERSION:
            logger.opt(colors=True).debug(
                f"检测到插件更新，已删除旧配置 <r>{cls.__config_name__}</r>")
            return {}
        return values


class Question(BaseModel):
    nums: list[int] = []
    solution: list[str] = []


def register(box: AyakaBox, n: int):
    if n == 24:
        def get_data():
            config = Config()
            return config.data_24
    else:
        def get_data():
            config = Config()
            return config.data_48

    @box.on_cmd(cmds=[f"{n}点"])
    async def _():
        '''启动游戏'''
        await box.start("run")
        await box.send(box.help)
        await set_q()

    box.set_close_cmds(cmds=["退出", "exit", "quit"])

    @box.on_cmd(cmds=["出题", "下一题", "next"], states=["run"])
    async def to_q():
        await box.set_state("出题")

    @box.on_immediate(state="出题")
    async def set_q():
        cache = box.get_data(Question)
        q = choice(list(get_data().keys()))
        nums = q.split(" ")
        solution = get_data()[q]
        cache.nums = [int(n) for n in nums]
        cache.solution = solution
        await box.send(f"{q}\n\nTIPS：本题至少有{len(solution)}种答案（使用不同的运算符）")
        await box.set_state("run")

    @box.on_cmd(cmds=["题目", "查看题目", "查看当前题目", "当前题目", "question"], states=["run"])
    async def _():
        cache = box.get_data(Question)
        nums = cache.nums
        solution = cache.solution
        q = " ".join(str(n) for n in nums)
        await box.send(f"{q}\n\nTIPS：本题至少有{len(solution)}种答案（使用不同的运算符）")

    @box.on_cmd(cmds=["答案", "answer"], states=["run"])
    async def _():
        cache = box.get_data(Question)
        nums = cache.nums
        solution = cache.solution

        if not nums:
            await box.send("请先出题")
            return

        info = "\n".join(solution)
        await box.send(info)
        await set_q()

    @box.on_text(states=["run"])
    async def _():
        '''请使用正确的表达式，例如 (1+2)*(3+3)'''
        cache = box.get_data(Question)
        nums = cache.nums
        if not nums:
            return

        exp = box.event.get_plaintext()

        # 运算
        r = calc(exp, nums)
        if isinstance(r, str):
            await box.send(r)
            return

        await box.send(f"{exp}={r}")

        if abs(r-n) > 0.0001:
            await box.send("错误")
            return

        await box.send("正确！")
        reward = Config().reward
        money = get_money(group_id=box.group_id, user_id=box.user_id)
        money.value += reward
        await box.send(f"奖励{reward}金")
        await box.set_state("出题")


def check_len(exp: str):
    '''拒绝长度异常的表达式'''
    return len(exp) <= 20


def pre_correct(exp: str):
    '''初步矫正表达式：移除空格，纠正操作符'''
    exp = exp.strip().replace("\\", "/").replace(" ", "")
    exp = exp.replace("x", "*").replace("^", "**")
    exp = re.sub(r"[（{【\[]", "(", exp)
    exp = re.sub(r"[）}】\]]", ")", exp)
    return exp


def check_brackets_close(exp: str):
    '''检查括号配对是否闭合'''
    cnt = 0
    for t in exp:
        if t == "(":
            cnt += 1
        elif t == ")":
            cnt -= 1
            if cnt < 0:
                return False
    return cnt == 0


def check_op(exp: str):
    '''检测无效操作符'''
    patt = re.compile(r"\*\*|\*|\+|-|/|\(|\)|\d+")
    return not patt.sub("", exp)


def split_exp(exp: str):
    '''分割表达式'''
    patt = re.compile(r"\*\*|\*|\+|-|/|\(|\)|\d+")
    ts: list[int | str] = []
    for t in patt.findall(exp):
        if t not in ["(", ")", "+", "-", "*", "/", "**"]:
            t = int(t)
        ts.append(t)
    return ts


def check_num(ts: list[str | int], nums: list[int]):
    '''检查是否使用指定数字'''
    nums_copy = [n for n in nums]
    for t in ts:
        if isinstance(t, int):
            if t not in nums_copy:
                return False
            nums_copy.remove(t)
    return True


def check_and_correct_op(ts: list[str | int]):
    '''补全缺失的*，检查错误组合'''

    _ts = [ts[0]]
    last = ts[0]

    for t in ts[1:]:
        # 数字 + (，补全*
        if isinstance(last, int) and t == "(":
            _ts.append("*")

        # (只能 + 数字或(
        elif last == "(" and isinstance(t, str) and t != "(":
            return

        # ) + (或数字，补全*
        elif last == ")" and (isinstance(t, int) or t == "("):
            _ts.append("*")

        # 其他操作符必定不 + )
        elif last in ["+", "-", "*", "/", "**"] and t == ")":
            return

        _ts.append(t)
        last = t
    return _ts


def mid2post(ts: list[str | int]):
    '''中缀表达式转后缀表达式'''
    ts.append("#")
    stack = ["#"]
    rs: list[str | int] = []

    _in = {
        "#": 0,
        "(": 1,
        "+": 2, "-": 2,
        "*": 4, "/": 4,
        "**": 6,
    }
    _out = {
        "#": 0,
        ")": 1,
        "+": 3, "-": 3,
        "*": 5, "/": 5,
        "**": 7,
        "(": 8,
    }

    for t in ts:
        # 数字直接计入结果
        if isinstance(t, int):
            rs.append(t)
            continue

        # 操作符判断优先级入栈
        d = _out[t] - _in[stack[-1]]

        # 若 out < in，则内部操作符优先级更高，出栈，计入结果，且循环判断
        # 注意：栈不可能通过此条件弹出至空，因为 # 对应 最小in = 最小out = 0
        while d < 0:
            rs.append(stack.pop())
            d = _out[t] - _in[stack[-1]]

        # 若 out > in，则外部操作符优先级更高，入栈
        if d > 0:
            stack.append(t)

        # 若 out == in，则优先级相同，出栈，且不计入结果
        else:
            stack.pop()

    return rs


def base_calc(n1: float, n2: float, op: str):
    '''计算数值，出错时抛出异常'''
    logger.debug(f"基本运算单元 {n1}{op}{n2}")

    if op == "*":
        return n1*n2

    # 除0自动抛出异常
    if op == "/":
        return n1 / n2

    if op == "+":
        return n1 + n2

    if op == "-":
        return n1 - n2

    if op == "**":
        # 阻断大指数运算
        if n1 > 100 or n2 > 100:
            raise
        return n1 ** n2

    # 未知操作符
    raise


def calc_post(ts: list[str | int]):
    '''计算后缀表达式'''
    ops: list[str] = []
    nums: list[float] = []
    for t in ts:
        if isinstance(t, str):
            ops.append(t)
        else:
            nums.append(float(t))

        if len(nums) >= 2 and ops:
            n2 = nums.pop()
            n1 = nums.pop()
            op = ops.pop()
            n = base_calc(n1, n2, op)

            # 中断过大的运算
            if n > 10000:
                raise

            nums.append(n)

    return nums[0]


def calc(exp, nums):
    '''计算表达式'''
    if not check_len(exp):
        return "表达式过长"

    exp = pre_correct(exp)

    if not check_brackets_close(exp):
        return "括号未闭合"

    if not check_op(exp):
        return "无效操作符"

    ts = split_exp(exp)

    if not check_num(ts, nums):
        return "没有使用指定数字"

    ts = check_and_correct_op(ts)

    if not ts:
        return "错误的表达式"

    ts = mid2post(ts)

    logger.debug(f"后缀表达式 {ts}")

    try:
        v = calc_post(ts)
    except:
        return "计算出错"

    return v


box_1 = AyakaBox("24点")
box_1.help = "加减乘除次方，5种运算符可用；给出4个1-9范围内的数字，请通过以上运算符算出24点"
register(box_1, 24)

box_2 = AyakaBox("48点")
box_2.help = "加减乘除次方，5种运算符可用；给出4个1-9范围内的数字，请通过以上运算符算出48点"
register(box_2, 48)
