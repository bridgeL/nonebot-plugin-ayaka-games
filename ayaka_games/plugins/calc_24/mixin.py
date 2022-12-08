from typing import List
from ayaka import AyakaApp, AyakaCache
from random import choice
from .utils import deal
from .data import config


class Question(AyakaCache):
    nums: List[int] = []
    solution: dict = {}


def register(app: AyakaApp, n: int):
    if n == 24:
        data = config.data_24
    else:
        data = config.data_48

    questions = list(data.keys())

    @app.on.idle()
    @app.on.command(f"{n}点")
    async def _(cache: Question):
        '''启动游戏'''
        await app.start()
        await app.send(app.help)
        await set_q(cache)

    @app.on.state()
    @app.on.command("退出", "exit", "quit")
    async def _():
        await app.close()

    @app.on.state()
    @app.on.command("出题", "下一题", "next")
    async def set_q(cache: Question):
        q = choice(questions)
        nums = q.split(" ")
        solution = data[q]
        cache.nums = [int(n) for n in nums]
        cache.solution = solution
        await app.send(f"{q}\n\nTIPS：本题至少有{len(solution)}种答案（使用不同的运算符）")

    @app.on.state()
    @app.on.command("题目", "查看题目", "查看当前题目", "当前题目", "question")
    async def _(cache: Question):
        nums = cache.nums
        solution = cache.solution
        q = " ".join(str(n) for n in nums)
        await app.send(f"{q}\n\nTIPS：本题至少有{len(solution)}种答案（使用不同的运算符）")

    @app.on.state()
    @app.on.command("答案", "answer")
    async def _(cache: Question):
        nums = cache.nums
        solution = cache.solution

        if not nums:
            await app.send("请先出题")
            return

        info = "\n".join(solution.values())
        await app.send(info)
        await set_q(cache)

    @app.on.state()
    @app.on.text()
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
