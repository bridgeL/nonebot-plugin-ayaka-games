from random import choice
from typing import Dict, List
from pydantic import BaseModel
from pypinyin import lazy_pinyin


class Dragon(BaseModel):
    name: str
    words: List[str]
    pinyin_dict: Dict[str, list] = {}

    def __init__(self, **data) -> None:
        super().__init__(**data)

        # 拼音速查表
        self.pinyin_dict: Dict[str, list] = {}
        for word in self.words:
            # 获取首字的拼音
            p = lazy_pinyin(word)[0]
            if p not in self.pinyin_dict:
                self.pinyin_dict[p] = []
            self.pinyin_dict[p].append(word)

    def dict(self, **data):
        data["exclude"] = {"pinyin_dict"}
        return super().dict(**data)

    def check(self, word: str):
        return word in self.words

    def next(self, word: str):
        # 获取末字的拼音
        p = lazy_pinyin(word)[-1]
        words: List[str] = self.pinyin_dict.get(p)
        if not words:
            return ""
        return choice(words)
