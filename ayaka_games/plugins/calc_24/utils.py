import ast
import re


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
