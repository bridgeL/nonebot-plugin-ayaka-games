from ayaka import *
import requests

app = AyakaApp('缩写翻译')
app.help = "fy <参数>"


@app.on_command(['fanyi', 'fy', '翻译'])
async def fanyi():
    if app.args:
        arg = str(app.args[0])
        response = requests.post(
            url='https://lab.magiconch.com/api/nbnhhsh/guess',
            data={'text': arg}
        )
        result = response.json()
        if result:
            result = result[0]
            if 'trans' in result:
                ans = ''
                for t in result["trans"]:
                    ans += t + ' '
                await app.send('[翻译]{0}'.format(ans))
            if 'inputting' in result:
                await app.send('可能是{0}'.format(result["inputting"]))
        else:
            await app.send('请求的API不稳定，请稍后重试')
    else:
        await app.send('没有输入参数')
