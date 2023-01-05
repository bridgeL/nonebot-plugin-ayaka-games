'''
    原神随机事件
'''
from random import choice
from typing import Literal
from ayaka import AyakaBox, AyakaConfig, BaseModel, slow_load_config

box = AyakaBox("原神随机事件")


class Group(BaseModel):
    type: Literal["Group"] = "Group"
    rules: list[str]
    parts: list["Part"]

    def get_value(self, rule: str = None, data: dict = None):
        params = {k: p.choice() for p in self.parts for k in p.names}

        # 内部参数 + 外部参数
        if data:
            params.update(data)

        # 内部规则 or 外部规则
        if not rule:
            if not self.rules:
                return ""
            rule = choice(self.rules)

        return rule.format(**params)


class Part(BaseModel):
    type: Literal["Part"] = "Part"
    names: list[str]
    values: list[str | Group]

    def choice(self):
        if not self.values:
            return ""
        value = choice(self.values)
        if isinstance(value, Group):
            return value.get_value()
        return value


# 很重要
Group.update_forward_refs()

# 默认配置
default_group = Group(rules=["{角色}在{地点}{心情}地{事件}", "{角色}和{角色2}在{地点}{心情}地{事件}"], parts=[
    Part(names=["角色", "角色2"], values=[
        "优菈", "阿贝多", "可莉", "温迪", "迪卢克", "琴", "莫娜", "空", "荧", "申鹤", "胡桃", "魈", "甘雨", "钟离", "刻晴", "七七", "神里绫人", "八重神子", "荒泷一斗", "珊瑚宫心海", "雷电将军", "宵宫", "神里绫华", "枫原万叶", "夜兰", "提纳里", "赛诺", "纳西妲", "流浪者", "埃洛伊", "罗莎莉亚", "迪奥娜", "芭芭拉", "雷泽", "安柏", "菲谢尔", "丽莎", "砂糖", "诺艾尔", "凯亚", "班尼特", "云堇", "烟绯", "辛焱", "北斗", "重云", "香菱", "行秋", "凝光", "久岐忍", "五郎", "托马", "九条裟罗", "早柚", "鹿野院平藏", "柯莱", "坎蒂丝", "莱依拉", "珐露珊", "米卡", "卡维", "迪希雅", "艾尔海森"
    ]),
    Part(names=["地点"], values=[
        "坠星山谷", "明冠山地", "苍风高地", "风啸山坡", "龙脊雪山", "碧水原", "琼玑野", "珉林", "云来海", "璃沙郊", "层岩巨渊", "鸣神岛", "神无冢", "清籁岛", "八酝岛", "海祇岛", "鹤观", "护世森", "道成林", "阿陀河谷", "桓那兰那", "二净甸", "善见地", "失落的苗圃", "下风蚀地", "上风蚀地", "列柱沙原", "海岛", "层岩巨渊地下矿区", "渊下宫"
    ]),
    Part(names=["心情"], values=["喜悦", "悲痛", "轻松", "狂喜", "郁闷", "尴尬", "生气"]),
    Part(names=["事件"], values=[
        "植树造林", "写论文", "开宝箱", "哭", "考试", "约会", "自娱自乐",
        Group(rules=["{动作}{对象}"], parts=[
            Part(names=["动作"], values=["打", "吃", "喝", "调查", "做", "抓"]),
            Part(names=["对象"], values=[
                "七圣召唤", "爆炎树", "三彩团子", "鸟蛋烧", "绯樱饼", "团子牛奶", "蒲烧鳗肉", "兽骨拉面", "绀田煮", "蟹黄壳壳烧", "串串三味", "金枪鱼寿司", "独眼大宝", "独眼小宝", "苹果酒", "鬼兜虫", "糖霜史莱姆"
            ])
        ])
    ]),
])

helps = '''
简单介绍：
1.每个句子都可以视为一个Group
2.Group由多个Part、以自定义的rule拼接而成，而每个Part都有自己的名字，通过名字来确定他们在拼接规则中的位置，例如rule = {名字}在{地点}做{动作}
3.rule可以有多个，Group随机选择一个rule进行拼接
4.Part内存有一个数据元素池，Part随机从数据元素池中抽取一个元素作为值
5.Part的数据元素池中的元素，可以是字符串，也可以是Group
6.开始套娃
'''.strip().split("\n")


@slow_load_config
class Config(AyakaConfig):
    __config_name__ = box.name
    helps: list[str] = helps
    group: Group = default_group


def get_value_with_custom_part(name, value):
    config = Config()
    return config.group.get_value(data={name: value})


def get_value():
    config = Config()
    return config.group.get_value()


@box.on_cmd(cmds=["原神随机事件"])
async def _():
    event = str(box.arg)
    if event:
        await box.send(get_value_with_custom_part("事件", event))
    else:
        await box.send(get_value())
