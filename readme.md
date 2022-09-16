# ayaka衍生插件 v0.0.3

基于ayaka开发的文字小游戏合集

- 印加宝藏 [@灯夜](https://github.com/lunexnocty/Meiri)
- 赌大小
- 原神接龙
- 成语接龙
- 祈祷nia
- 背包

<b>注意：由于更新pypi的readme.md需要占用版本号，因此其readme.md可能不是最新的，强烈建议读者前往[github仓库](https://github.com/bridgeL/nonebot-plugin-ayaka-games)以获取最新版本的帮助</b>

# 更新记录

<details>
<summary>更新记录</summary>

版本 | 备注
-|-
0.0.4 | 修复了单个插件错误导致其他插件无法导入的问题

</details>

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
