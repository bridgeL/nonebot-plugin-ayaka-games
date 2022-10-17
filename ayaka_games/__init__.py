# 导入全部插件
from importlib import import_module
from pathlib import Path
from ayaka import logger

paths = Path(__file__).parent.iterdir()

for p in paths:
    name = p.stem
    if name.startswith("_") or name.startswith("."):
        continue
    module_name = f"ayaka_games.{name}"
    try:
        import_module(module_name)
        logger.success(f"{name} 导入成功")
    except:
        logger.exception(f"{name} 导入失败")
