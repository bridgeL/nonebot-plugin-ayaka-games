'''
    成语查询
'''
from random import sample
from nonebot import on_regex
from ayaka import AyakaBox, load_data_from_file
from nonebot.params import RegexGroup
from .data import downloader

box = AyakaBox("成语查询")
box.help = '''
有效提高群文学氛围

数据来源：成语大全（20104条成语数据）
'''

search_dict = {}


@downloader.on_finish
async def finish():
    global search_dict
    path = downloader.BASE_DIR / "成语词典.json"
    search_dict = load_data_from_file(path)


async def show_word(word: str):
    if word in search_dict:
        await box.send(search_dict[word])
    else:
        await box.send("没有找到相关信息")


@box.on_cmd(cmds="查询成语")
async def handle_1():
    '''查询指定成语的意思'''
    word = box.arg.extract_plain_text()
    await show_word(word)

MATCHER = on_regex(r"(.*?)是(不是)?成语吗?", rule=box.rule())


@MATCHER.handle()
async def handle_2(args: tuple = RegexGroup()):
    word = args[0]
    await show_word(word)


@box.on_cmd(cmds="搜索成语")
async def handle_3():
    '''搜索所有相关的成语，可输入多个关键词更准确'''
    args = [arg for arg in box.args if isinstance(arg, str)]

    if not args:
        await box.send("没有输入关键词")
        return

    words = []
    for _word in search_dict:
        for arg in args:
            if arg not in _word:
                break
        else:
            words.append(_word)

    if not words:
        await box.send("没有找到相关信息")
        return

    n = len(words)
    infos = [
        f"搜索关键词：{args}",
        f"共找到{n}条相关信息"
    ]
    if n > 100:
        infos.append("数量过多，仅展示随机抽取的100条")
        words = sample(words, 100)
    infos.append("\n".join(words))
    infos.append("可以使用 查询成语 <成语> 来查看进一步解释")
    await box.send_many(infos)
