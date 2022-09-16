# ayaka衍生插件

基于ayaka开发的文字小游戏合集

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
