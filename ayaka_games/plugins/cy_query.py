'''
    成语查询
'''
import json
from pydantic import Field
from ayaka import AyakaApp, AyakaInput, AyakaLargeConfig
from ayaka.extension import singleton, run_in_startup
from .utils import get_path

app = AyakaApp("成语查询")
app.help = '''有效提高群文学氛围'''


def get_data():
    path = get_path("data", "chengyu.json")
    with path.open("r", encoding="utf8") as f:
        chengyu_meaning_dict = json.load(f)
    return chengyu_meaning_dict


@run_in_startup
@singleton
class Config(AyakaLargeConfig):
    __app_name__ = app.name
    data: dict = Field(default_factory=get_data)


class WordInput(AyakaInput):
    word: str = Field(description="成语")


@app.on.idle()
@app.on.command("查询成语", "成语查询")
async def handle(data: WordInput):
    word = data.word
    search_dict = Config().data
    if word in search_dict:
        await app.send(search_dict[word])
    else:
        await app.send("没有找到相关信息")
