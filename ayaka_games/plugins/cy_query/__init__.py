'''
    成语查询
'''
from pydantic import Field
from ayaka import AyakaApp, AyakaInput
from .data import config

app = AyakaApp("成语查询")
app.help = '''有效提高群文学氛围'''

search_dict = config.data


class UserInput(AyakaInput):
    word: str = Field(description="成语")


@app.on.idle()
@app.on.command("查询成语", "成语查询")
async def handle(data: UserInput):
    word = data.word

    if word in search_dict:
        await app.send(search_dict[word])
    else:
        await app.send("没有找到相关信息")
