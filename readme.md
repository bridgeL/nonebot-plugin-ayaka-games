# ayaka衍生插件

基于ayaka开发的文字小游戏合集

- incan 印加宝藏 [@灯夜](https://github.com/lunexnocty/Meiri)
- bet 赌大小
- 原神接龙
- 成语接龙
- 祈祷nia

<b>注意：由于更新pypi的readme.md需要占用版本号，因此其readme.md可能不是最新的，强烈建议读者前往[github仓库](https://github.com/bridgeL/nonebot-plugin-ayaka-games)以获取最新版本的帮助</b>

## How to start

首先需要安装 ayaka插件 `poetry add nonebot-plugin-ayaka`

安装 `poetry add nonebot-plugin-ayaka-games`

修改nonebot2 在 `bot.py` 中写入 

```python
# 先加载ayaka
nonebot.load_plugin("ayaka")
nonebot.load_plugin("ayaka_games")
```

## Documentation

See [nonebot-plugin-ayaka](https://github.com/bridgeL/nonebot-plugin-ayaka)
