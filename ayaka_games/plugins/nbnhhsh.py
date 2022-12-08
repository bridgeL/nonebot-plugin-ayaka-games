from pydantic import Field
from ayaka import AyakaApp, AyakaInput
import requests


app = AyakaApp('缩写翻译')


class AbbrInput(AyakaInput):
    abbr: str = Field(description="缩写")


@app.on.idle()
@app.on.command('fanyi', 'fy', '翻译')
async def fanyi(data: AbbrInput):
    word = data.abbr
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
