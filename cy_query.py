'''
    成语查询
'''
from random import sample
from nonebot import on_regex
from ayaka import AyakaBox, AyakaConfig, slow_load_config, Field
from nonebot.params import RegexGroup
from .data import load_data

box = AyakaBox("成语查询")
box.help = '''
有效提高群文学氛围

数据来源：成语大全（20104条成语数据）
'''


@slow_load_config
class Config(AyakaConfig):
    __config_name__ = box.name
    words: dict = Field(default_factory=lambda: load_data("chengyu.json"))


async def show_word(word: str):
    config = Config()
    search_dict = config.words
    if word in search_dict:
        await box.send(search_dict[word])
    else:
        await box.send("没有找到相关信息")


@box.on_cmd(cmds="查询成语")
async def handle():
    '''查询指定成语的意思'''
    word = box.arg.extract_plain_text()
    await show_word(word)

MATCHER = on_regex(r"(.*?)是(不是)?成语吗?", rule=box.rule())


@MATCHER.handle()
async def handle(args: tuple = RegexGroup()):
    word = args[0]
    await show_word(word)


@box.on_cmd(cmds="搜索成语")
async def handle():
    '''搜索所有相关的成语，可输入多个关键词更准确'''
    config = Config()
    args = [arg for arg in box.args if isinstance(arg, str)]

    search_dict = config.words

    words = []
    for _word in search_dict:
        for arg in args:
            if arg not in _word:
                break
        else:
            words.append(_word)

    if not words:
        await box.send("没有找到相关信息")

    n = len(words)
    infos = [f"共找到{n}条相关信息"]
    if n > 100:
        infos.append("数量过多，仅展示随机抽取的100条")
        words = sample(words, 100)
    if words:
        infos.append("\n".join(words))
    await box.send_many(infos)
