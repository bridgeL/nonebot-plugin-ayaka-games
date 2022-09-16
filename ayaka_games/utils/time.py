'''便捷时间转换'''

import time


def get_time_i():
    '''获得当前时间戳，单位为妙'''
    return int(time.time())


def get_time_s(format: str = '%Y/%m/%d %H:%M:%S'):
    '''获得当前时间字符串，格式由用户自定义'''
    return time.strftime(format, time.localtime())


def time_s2i(time_s: str, format: str = '%Y/%m/%d %H:%M:%S'):
    '''将时间字符串转换为时间戳，需要用户提供其格式'''
    t = time.strptime(time_s, format)
    return int(time.mktime(t))


def time_i2s(time_i: int, format: str = '%Y/%m/%d %H:%M:%S'):
    '''将时间戳转换为时间字符串，格式由用户自定义'''
    t = time.localtime(time_i)
    return time.strftime(format, t)


def time_i_to_date_i(time_i: int):
    '''将时间戳转换为日期编号

    日期编号起点为2000年1月1日'''
    return int((time_i - 1640966400)/86400)


def date_i_to_time_i(date_i: int):
    '''将日期编号转换为时间戳'''
    return date_i*86400 + 1640966400


def time_i_to_local_seconds(time_i: int):
    '''将时间戳转换为从当地0:00:00开始计时的秒数'''
    return (time_i - 57600) % 86400
