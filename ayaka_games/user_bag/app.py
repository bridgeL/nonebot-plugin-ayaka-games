from ayaka import AyakaApp

app = AyakaApp("背包")
app.help = '''背包
- money/财富 查看拥有财富
- mana 查看拥有玛娜
- mana <数字> 购买指定数量的玛娜，可以为负数，相当于卖出
'''


class User:
    '''仅可在群聊中使用'''

    def __init__(self, uid: int) -> None:
        self.storage = app.group_storage(f"{uid}.json", default={})

    def get_all(self) -> dict:
        return self.storage.load()

    def get(self, name: str, default=None):
        data = self.get_all()
        d = data.get(name)
        if d is not None:
            return d

        if default is None:
            return

        self.set(name, default)
        return default

    def set(self, name: str, d):
        data = self.get_all()
        data[name] = d
        self.storage.save(data)
