# ayaka衍生插件 v0.0.5

基于ayaka开发的文字小游戏合集（共计10个）

## 基础插件
提供金钱管理功能，让游戏更有目的性
- 背包
- 签到

## 文字游戏插件
1. 印加宝藏 [@灯夜](https://github.com/lunexnocty/Meiri)
2. 原神接龙
3. 成语接龙
4. 赌大小
5. 祈祷nia
6. 发癫生成器
7. bingo~

<b>注意：由于更新pypi的readme.md需要占用版本号，因此其readme.md可能不是最新的，强烈建议读者前往[github仓库](https://github.com/bridgeL/nonebot-plugin-ayaka-games)以获取最新版本的帮助</b>

# 更新记录

<details>

<summary>更新记录</summary>

版本 | 备注
-|-
0.0.4 | 修复了单个插件错误导致其他插件无法导入的问题
0.0.5 | 新增插件bingo，checkin，template

</details>

## How to start

首先需要安装 ayaka插件 `poetry add nonebot-plugin-ayaka`

之后安装 `poetry add nonebot-plugin-ayaka-games`

修改nonebot2 在 `bot.py` 中写入 

```python
# 先加载ayaka
nonebot.load_plugin("ayaka")
nonebot.load_plugin("ayaka_games")
```

## Documentation

前置插件 [nonebot-plugin-ayaka](https://github.com/bridgeL/nonebot-plugin-ayaka)

## 特别感谢

[@灯夜](https://github.com/lunexnocty/Meiri) 大佬的插件蛮好玩的~
