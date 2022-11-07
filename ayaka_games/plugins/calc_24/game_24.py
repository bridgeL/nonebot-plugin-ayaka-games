from ayaka import AyakaApp
from .mixin import register

app = AyakaApp("24点")
app.help = "加减乘除次方，5种运算符可用；给出4个1-13范围内的数字，请通过以上运算符算出24点"
register(app, 24)
