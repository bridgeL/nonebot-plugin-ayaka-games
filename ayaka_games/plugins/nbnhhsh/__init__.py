from ayaka import AyakaApp
import requests


app = AyakaApp('缩写翻译')
app.help = '''
fy <参数> 缩写翻译
'''


@app.on.idle()
@app.on.command('fanyi', 'fy', '翻译')
async def fanyi():
    try:
        word = str(app.args[0])
    except:
        await app.send('参数缺失')
        return

    response = requests.post(
        url='https://lab.magiconch.com/api/nbnhhsh/guess',
        data={'text': word}
    )
    result = response.json()
    if not result:
        await app.send('API不稳定，请稍后重试')

    result = result[0]
    if 'trans' in result:
        ans = ''
        for t in result["trans"]:
            ans += t + ' '
        await app.send('[翻译]{0}'.format(ans))

    if 'inputting' in result:
        await app.send('可能是{0}'.format(result["inputting"]))
