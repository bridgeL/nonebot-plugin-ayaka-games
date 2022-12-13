from pathlib import Path


def get_path(*args: str):
    return Path(__file__).parent.joinpath(*args)
