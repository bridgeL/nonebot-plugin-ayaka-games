'''
    成语查询
'''
from ayaka import AyakaApp

app = AyakaApp("成语查询")
app.help = '''有效提高群文学氛围'''


search_dict: dict = app.storage.plugin_path().json("data", {}).load()


@app.on.idle()
@app.on.command("查询成语")
async def handle():
    '''<成语>'''
    try:
        word = str(app.args[0])
    except:
        await app.send("参数缺失")
        return

    if word in search_dict:
        await app.send(search_dict[word])
    else:
        await app.send("没有找到相关信息")
