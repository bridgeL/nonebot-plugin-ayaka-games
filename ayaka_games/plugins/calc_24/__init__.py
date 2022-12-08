'''
    注意，本插件使用了eval ！！！
  
    尽管已有所限制，但插件作者不保证代码已排除了所有注入风险！！
'''

from ayaka import AyakaApp
from .mixin import register

app_1 = AyakaApp("24点")
app_1.help = "加减乘除次方，5种运算符可用；给出4个1-13范围内的数字，请通过以上运算符算出24点"
register(app_1, 24)

app_2 = AyakaApp("48点")
app_2.help = "加减乘除次方，5种运算符可用；给出4个1-13范围内的数字，请通过以上运算符算出48点"
register(app_2, 48)
