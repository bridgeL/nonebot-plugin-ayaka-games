from ..bag import get_user_prop, set_user_prop, get_money, change_money


def get_mana(uid) -> int:
    return get_user_prop("玛娜", uid, 10)


def set_mana(uid, mana) -> int:
    return set_user_prop("玛娜", uid, mana)


def change_mana(uid, diff):
    return set_mana(uid, get_mana(uid) + diff)


def buy_mana(uid, num):
    money = get_money(uid)
    if money < num*1000:
        return False, money, 0
    money = change_money(uid, -num*1000)
    mana = change_mana(uid, num)
    return True, money, mana


def sold_mana(uid, num):
    mana = get_mana(uid)
    if mana < num:
        return False, 0, mana
    money = change_money(uid, num*1000)
    mana = change_mana(uid, -num)
    return True, money, mana
