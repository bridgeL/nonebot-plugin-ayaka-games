from ayaka import AyakaApp
from random import choice
from .utils import deal


def register(app: AyakaApp, n: int):
    file = app.storage.plugin_path().json(f"{n}点题库")
    data: dict = file.load()
    questions = list(data.keys())

    @app.on.idle()
    @app.on.command(f"{n}点")
    async def _():
        '''启动游戏'''
        await app.start()
        await app.send(app.help)
        await set_q()

    @app.on.state()
    @app.on.command("退出", "exit", "quit")
    async def _():
        await app.close()

    @app.on.state()
    @app.on.command("出题", "下一题", "next")
    async def set_q():
        q = choice(questions)
        ans = data[q]
        nums = q.split(" ")
        nums = [int(n) for n in nums]
        app.cache.data = [nums, ans]
        await app.send(f"{q}\n\nTIPS：本题至少有{len(ans)}种答案（使用不同的运算符）")

    @app.on.state()
    @app.on.command("题目", "查看题目", "查看当前题目", "当前题目")
    async def _():
        
        nums, solution = app.cache.data
        q = " ".join(str(n) for n in nums)
        await app.send(f"{q}\n\nTIPS：本题至少有{len(solution)}种答案（使用不同的运算符）")

    @app.on.state()
    @app.on.command("答案")
    async def _():
        
        if not app.cache.data:
            await app.send("请先出题")
            return

        nums, solution = app.cache.data
        info = "\n".join(solution.values())
        await app.send(info)

        app.cache.data = None

    @app.on.state()
    @app.on.text()
    async def _():
        '''请使用正确的表达式，例如 (1+2)*(3+3)'''
        if not app.cache.data:
            return

        nums, solution = app.cache.data
        try:
            exp, r = deal(app.event.get_plaintext(), nums)
        except Exception as e:
            code, info = e.args
            await app.send(info)
            return

        r = "正确！" if abs(r-n) < 0.1 else "错误"
        await app.send(exp + "\n" + r)
