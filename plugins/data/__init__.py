from pathlib import Path
from ayaka import load_data_from_file


def load_data(*parts: str):
    '''获取指定文件的数据'''
    return load_data_from_file(Path(__file__).parent.joinpath(*parts))
