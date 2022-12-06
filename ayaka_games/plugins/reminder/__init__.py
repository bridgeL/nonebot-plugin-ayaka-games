'''
    留言
'''

# 有bug详见scripts/bug/reminder.ini
import datetime
from typing import List, Union
from pydantic import BaseModel, Field
from ayaka import AyakaApp, MessageSegment, AyakaInputModel, msg_type

app = AyakaApp("留言")
app.help = "留言，在TA再次在群里发言时发送留言内容"


msg_at = msg_type("at")


class UserInput(AyakaInputModel):
    value: Union[msg_at, int, str] = Field(description="留言目标的QQ号/名称/@xx")

    def is_uid(self):
        return isinstance(self.value, (MessageSegment, int))

    def get_value(self):
        if isinstance(self.value, MessageSegment):
            return int(self.value.data["qq"])
        if isinstance(self.value, str) and self.value.startswith("@"):
            return self.value[1:]
        return self.value


class ReminderMsg(BaseModel):
    uid: int
    name: str
    content: str
    put_time: str
    deadline: int


class Reminder(BaseModel):
    uid: int
    msgs: List[ReminderMsg]


class ReminderManager:
    def __init__(self) -> None:
        self.file = app.storage.group_path().json("reminder.json", [])
        data = self.file.load()
        self.reminders = [Reminder(**d) for d in data]

    def save(self):
        self.file.save([r.dict() for r in self.reminders])

    def get_reminder(self, r_uid):
        for s in self.reminders:
            if s.uid == r_uid:
                return s

    def add_reminder(self, r_uid):
        reminder = Reminder(uid=r_uid, msgs=[])
        self.reminders.append(reminder)
        self.save()
        return reminder

    def add_message(self, r_uid, uid, name, content):
        reminder = self.get_reminder(r_uid)
        if not reminder:
            reminder = self.add_reminder(r_uid)
        now = datetime.datetime.now()
        put_time = now.strftime("%Y-%m-%d %H:%M:%S")
        # 保留3天
        deadline = int(now.timestamp()) + 3*86400
        msg = ReminderMsg(
            uid=uid, name=name, content=content,
            put_time=put_time,
            deadline=deadline,
        )
        reminder.msgs.append(msg)
        self.save()

    def remove_reminder(self, r: Reminder):
        self.reminders.remove(r)
        self.save()


def get_reminder_manager() -> ReminderManager:
    if not app.cache.reminder_manager:
        app.cache.reminder_manager = ReminderManager()
    return app.cache.reminder_manager


@app.on.idle()
@app.on.text()
async def check_reminder():
    now = datetime.datetime.now()
    time = int(now.timestamp())

    reminder_manager = get_reminder_manager()
    r = reminder_manager.get_reminder(app.user_id)
    if not r:
        return

    reminder_manager.remove_reminder(r)

    # 删除过期的消息
    msgs = [msg for msg in r.msgs if msg.deadline >= time]

    if not msgs:
        return

    items = [f"[{app.user_name}]收到的留言"]
    for msg in msgs:
        items.append(msg.put_time)
        items.append(MessageSegment.node_custom(
            user_id=msg.uid,
            nickname=msg.name,
            content=msg.content
        ))

    await app.send_many(items)


@app.on.idle()
@app.on.command("留言")
async def start_reminder():
    await app.start("留言.输入留言对象")
    app.cache.uid = app.user_id
    await app.send("请输入留言对象：用户名/uid/@")


@app.on.state("留言")
@app.on.command("exit", "退出")
@app.on_deep_all()
async def app_exit():
    await app.close()


@app.on.state("留言.输入留言对象")
@app.on.text()
@app.on_model(UserInput)
async def set_uid():
    if app.cache.uid != app.user_id:
        return

    data: UserInput = app.model_data
    users = await app.bot.get_group_member_list(group_id=app.group_id)
    value = data.get_value()

    if data.is_uid():
        for user in users:
            uid = user["user_id"]
            if uid == value:
                name = user["card"] or user["nickname"]
                break
        else:
            uid = 0
    else:
        for user in users:
            name = user["card"] or user["nickname"]
            if name == value:
                uid = user["user_id"]
                break
        else:
            uid = 0

    if not uid:
        await app.send("查无此人")
        return

    await app.send(f"留言给[{name}]({uid})")
    app.cache.r_uid = uid
    await app.send("请输入留言内容")
    await app.goto("留言.输入留言内容")


@app.on.state("留言.输入留言内容")
@app.on.text()
async def set_content():
    if app.cache.uid != app.user_id:
        return

    r_uid = app.cache.r_uid
    content = str(app.arg)
    reminder_manager = get_reminder_manager()
    reminder_manager.add_message(r_uid, app.user_id, app.user_name, content)
    await app.send("留言成功！")
    await app.close()
