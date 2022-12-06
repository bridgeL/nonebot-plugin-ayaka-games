'''
    成语查询
'''
from pydantic import Field
from ayaka import AyakaApp, AyakaInputModel

app = AyakaApp("成语查询")
app.help = '''有效提高群文学氛围'''


class UserInput(AyakaInputModel):
    word: str = Field(description="成语")


search_dict: dict = app.storage.plugin_path().json("data", {}).load()


@app.on.idle()
@app.on.command("查询成语", "成语查询")
@app.on_model(UserInput)
async def handle():
    data: UserInput = app.model_data
    word = data.word

    if word in search_dict:
        await app.send(search_dict[word])
    else:
        await app.send("没有找到相关信息")
