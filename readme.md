# ayaka文字小游戏合集 v0.1.3

基于ayaka开发的文字小游戏合集（共计10个）

任何问题请发issue

<b>注意：由于更新pypi的readme.md需要占用版本号，因此其readme.md可能不是最新的，强烈建议读者前往[github仓库](https://github.com/bridgeL/nonebot-plugin-ayaka-games)以获取最新版本的帮助</b>

1. 背包
2. 签到
3. 印加宝藏 [@灯夜](https://github.com/lunexnocty/Meiri)
4. 原神接龙
5. 成语接龙
6. b站视频链接分析
7. bingo
8. 生成糊文字截图
9. 缩写翻译
10. b站up动态推送

# 更新记录

<details>

<summary>更新记录</summary>

## 0.1.0 
适配0.3.x版本的ayaka插件

## 0.1.1
修复了checkin失效的问题

## 0.1.2
更换了加载插件的方式

## 0.1.3
增减了部分插件

</details>

# How to start

## 安装 ayaka

安装 [前置插件](https://github.com/bridgeL/nonebot-plugin-ayaka) 

`poetry add nonebot-plugin-ayaka`


## 安装 本插件

安装 本插件

`poetry add nonebot-plugin-ayaka-games`

修改nonebot2  `bot.py` 

```python
# 导入ayaka_games插件
nonebot.load_plugin("ayaka_games")
```

## 导入数据

将[本仓库](https://github.com/bridgeL/nonebot-plugin-ayaka-games)的data文件夹，放到nonebot的工作目录下

之后运行nonebot即可

# 特别感谢

[@灯夜](https://github.com/lunexnocty/Meiri) 大佬的插件蛮好玩的~
