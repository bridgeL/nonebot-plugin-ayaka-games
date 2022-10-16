from ayaka import AyakaApp, MessageSegment, get_new_page

app = AyakaApp("好糊啊")
app.help = '''生成一张高清文字截图
- blur 高清
- bblur 超清
- bbblur 蓝光
- bbbblur 4k
'''

@app.on_command(["blur","bblur","bbblur", "bbbblur"])
async def _():
    text = "细" if not app.args else str(app.args[0])
    if app.cmd == "blur":
        n = 1
    elif app.cmd == "bblur":
        n = 3
    elif app.cmd == "bbblur":
        n = 5
    else:
        n = 7
    code = f'''
<span id="main" style="padding:20px; filter: blur({n}px); font-size: 60px; word-break: keep-all;">
    {text}
</span>
'''
    ht_path = app.plugin_storage("test", suffix=".html").path.absolute()
    with ht_path.open("w+", encoding="utf8") as f:
        f.write(code)

    path = app.plugin_storage("test", suffix=".png").path.absolute()
    async with get_new_page() as page:
        await page.goto(f"file://{ht_path}")
        await page.locator("#main").screenshot(path=path)
    image = MessageSegment.image(path)
    await app.send(image)
