from random import sample, seed, shuffle
from string import digits, ascii_lowercase, ascii_uppercase
from time import time

# 初始化随机数种子
seed(time())

# 随机数库
chars_bin = list(digits + ascii_lowercase + ascii_uppercase)
for i in range(10):
    shuffle(chars_bin)


def create_id(num=6) -> str:
    '''生成6位id'''
    return ''.join(sample(chars_bin, num))


def uuid8() -> str:
    return create_id(8)


def uuid6() -> str:
    return create_id(6)
