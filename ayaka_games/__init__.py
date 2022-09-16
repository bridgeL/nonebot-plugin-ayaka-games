# 导入全部插件
from importlib import import_module
from pathlib import Path

paths = Path(__file__).parent.iterdir()

for p in paths:
    name = p.stem
    if name.startswith("_") or name.startswith("."):
        continue
    import_module(f"ayaka_games.{name}")
