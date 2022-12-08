'''
    留言
'''
import datetime
from typing import List
from pydantic import BaseModel, Field
from ayaka import AyakaApp, MessageSegment,  AyakaGroupDB, AyakaCache
from .utils import UserInput, get_uid_name

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


class UserReminder(AyakaGroupDB):
    __table_name__ = "reminder"
    reminders: List[Reminder] = Field([], extra=AyakaGroupDB.__json_key__)

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


UserReminder.create_table()


class ReminderCache(AyakaCache):
    uid: int = 0
    r_uid: int = 0


@app.on.idle()
@app.on.text()
async def check_reminder():
    now = datetime.datetime.now()
    time = int(now.timestamp())

    reminder_manager = await UserReminder.create(app)
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
async def start_reminder(cache: ReminderCache):
    await app.start("输入留言对象")
    cache.uid = app.user_id
    await app.send("请输入留言对象：用户名/uid/@")


@app.on.state()
@app.on.command("exit", "退出")
@app.on_deep_all()
async def app_exit():
    await app.close()


@app.on.state("输入留言对象")
@app.on.text()
async def set_uid(data: UserInput, cache: ReminderCache):
    if cache.uid != app.user_id:
        return

    uid, name = await get_uid_name(app, data)

    if not uid:
        await app.send("查无此人")
        return

    await app.send(f"留言给[{name}]({uid})")
    cache.r_uid = uid
    await app.send("请输入留言内容")
    await app.goto("输入留言内容")


@app.on.state("输入留言内容")
@app.on.text()
async def set_content(cache: ReminderCache):
    if cache.uid != app.user_id:
        return

    r_uid = cache.r_uid
    content = str(app.arg)
    reminder_manager = await UserReminder.create(app)
    reminder_manager.add_message(r_uid, app.user_id, app.user_name, content)
    await app.send("留言成功！")
    await app.close()
