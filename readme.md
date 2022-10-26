# ayaka文字小游戏合集 v0.2.0

基于ayaka开发的文字小游戏合集（预计10个）

任何问题请发issue

<b>注意：由于更新pypi的readme.md需要占用版本号，因此其readme.md可能不是最新的，强烈建议读者前往[github仓库](https://github.com/bridgeL/nonebot-plugin-ayaka-games)以获取最新版本的帮助</b>

# 快速了解

## 基础功能
1. 背包
2. 签到

## 游戏
1. 印加宝藏 [@灯夜](https://github.com/lunexnocty/Meiri)
2. 接龙（多题库可选，原神/成语）
3. bingo
4. 谁是卧底
5. 抢30
6. mana
7. 加一秒

# How to start

## 安装 ayaka

安装基础插件

https://github.com/bridgeL/nonebot-plugin-ayaka

## 安装 本插件

安装本插件

`poetry add nonebot-plugin-ayaka-games`

修改nonebot2  `bot.py` 

```python
# 导入ayaka_games插件
nonebot.load_plugin("ayaka_games")
```

## 导入数据

将本仓库的data文件夹，放到nonebot的工作目录下

之后运行nonebot即可

# 详细帮助

启动bot后，可以使用help指令获取

## 印加宝藏
```
   指令列表: 
   - incan 启动应用
   - [start/run] 开始游戏
   - [join] 加入游戏
   - [status] 查看状态
   - [go/back] 前进/撤退
   - [rule/doc] 查看规则
   - [exit/quit] 退出
```
## 接龙
```
  接龙，在聊天时静默运行

  管理指令：
  - 接龙 进入管理面板
  - use <词库名称> 使用指定词库
  - unuse <词库名称> 关闭指定词库
  - list 列出所有词库
  - data 展示你的答题数据
  - rank 展示排行榜
  - exit 退出管理面板
```
## bingo
```
  经典小游戏
  - b <数字> 花费100金打开一张卡，当卡片练成一整行、一整列或一整条对角线时，获得200*n金的奖励
  - bb <数字> 免费生成一张新的bingo表，默认大小为4
```
## 谁是卧底
```
  至少4人游玩，游玩前请加bot好友，否则无法通过私聊告知关键词

  参与玩家的群名片不要重名，否则会产生非预期的错误=_=||

  卧底只有一个
  - 谁是卧底 打开应用
  - help/帮助 查看帮助
  - exit/退出 关闭应用

  [room] 房间已建立，正在等待玩家加入...
  - join/加入
  - leave/离开
  - start/begin/开始
  - info/信息 展示房间信息
  - exit/退出 关闭游戏
    
  [play] 游戏正在进行中...
  - vote <at> 请at你要投票的对象，一旦投票无法更改
  - info/信息 展示投票情况
  - force_exit 强制关闭游戏，有急事可用
```
## 抢30
```
  至少2人游玩，一局内进行多轮叫牌，谁最先达到或超过30点谁获胜

  总共52张牌，直到全部用完后才会洗牌，只要不退出游戏，下局的牌库将继承上局

  首轮所有人筹码为10，每轮所有人筹码+1
  - 抢30 打开应用
  - help/帮助 查看帮助
  - exit/退出 关闭应用
    
  [room] 房间已建立，正在等待玩家加入...
  - join/加入
  - leave/离开
  - start/begin/开始
  - info/信息 展示房间信息
  - exit/退出 关闭游戏
    
  [play] 游戏正在进行中...
  - 数字 报价叫牌，要么为0，要么比上一个人高，如果全员报价为0，则本轮庄家获得该牌
  - info/信息 展示当前牌、所有人筹码、报价
  - force_exit 强制关闭游戏，有急事可用
```
## mana
```
  ===== m a n a =====
  欢愉、悼亡、深渊、智慧
  ===== ======= =====

  - 祈祷 <数字> 花费n玛娜，祈求神的回应
  - 占卜 花费1玛娜，感受神的呼吸
```

## 加一秒

```
  每人初始时间值为0
  每有3个不同的人执行一次或若干次加1，boss就会完成蓄力，吸取目前时间值最高的人的时间，如果有多人，则均吸取1点
  boss时间值>=10时，游戏结束，时间值<=boss的人中，时间值最高的人获胜，一切重置
  - 加一加 启动游戏
  - exit/退出 退出游戏（数据保留）

  游戏内指令：
  - +1 让你的时间+1
  - 我的 查看你目前的时间
  - boss 查看boss的时间和能量
  - 全部 查看所有人参与情况，以及boss的时间和能量
```

# 特别感谢

[@灯夜](https://github.com/lunexnocty/Meiri) 大佬的插件蛮好玩的~

