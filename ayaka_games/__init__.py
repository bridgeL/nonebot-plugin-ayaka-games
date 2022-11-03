# 导入全部插件
import re
from pathlib import Path
from importlib import import_module
from loguru import logger

work_path = Path.cwd().absolute()

# 判断是否在工作目录下
under_work_path = work_path in Path(__file__).parents

# root_path
root_path = work_path if under_work_path \
    else Path(__file__).parent.parent.absolute()

plugins_path = Path(__file__).parent / "plugins"

for p in plugins_path.iterdir():
    if p.stem.startswith("_"):
        continue
    name = p.absolute().relative_to(root_path)
    name = re.sub(r"\\|/", ".", str(name))
    try:
        import_module(name)
        logger.success(f"导入成功 {name}")
    except:
        logger.warning(f"导入失败 {name}")
