'''
    成语查询
'''
from ayaka import AyakaBox, AyakaConfig, run_in_startup, Field
from .data import load_data

box = AyakaBox("成语查询")
# box.help = '''有效提高群文学氛围'''


class Config(AyakaConfig):
    __config_name__ = box.name
    words: dict = Field(default_factory=lambda: load_data("chengyu.json"))


config: Config = None


@run_in_startup
async def init():
    global config
    config = Config()


@box.on_cmd(cmds=["查询成语", "成语查询"])
async def handle():
    word = box.arg.extract_plain_text()
    search_dict = config.words
    if word in search_dict:
        await box.send(search_dict[word])
    else:
        await box.send("没有找到相关信息")
