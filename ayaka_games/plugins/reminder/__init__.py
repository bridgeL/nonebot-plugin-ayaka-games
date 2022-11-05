'''
    留言
'''

# 有bug详见scripts/bug/reminder.ini
import datetime
from typing import List

from pydantic import BaseModel
from ayaka import AyakaApp, MessageSegment
from .utils import GroupUserFinder

app = AyakaApp("留言")
app.help = "留言，在TA再次在群里发言时发送留言内容"


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
async def app_exit():
    await app.close()


@app.on.state("留言.输入留言对象")
@app.on.text()
async def set_uid():
    if app.cache.uid != app.user_id:
        return

    group_user_finder = GroupUserFinder(app.bot, app.group_id)
    user = await group_user_finder.get_user_by_segment(app.args[0])
    if not user:
        await app.send("查无此人")
        return

    r_uid = user["user_id"]
    r_name = user["card"] or user["nickname"]
    await app.send(f"留言给[{r_name}]({r_uid})")
    app.cache.r_uid = r_uid
    await app.send("请输入留言内容")
    app.state = "留言.输入留言内容"


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
