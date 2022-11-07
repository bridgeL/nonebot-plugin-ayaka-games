# 导入全部插件
import re
from pathlib import Path
from importlib import import_module
from ayaka import logger

work_path = Path.cwd().absolute()
file_path = Path(__file__)

# 判断是否在工作目录下
if work_path in file_path.parents:
    root_path = work_path
else:
    root_path = file_path.parent.parent.absolute()

plugins_path = file_path.parent / "plugins"

for p in plugins_path.iterdir():
    if p.stem.startswith("_"):
        continue
    name = p.absolute().relative_to(root_path)
    name = re.sub(r"\\|/", ".", str(name))
    short_name = name.split(".")[-1]
    try:
        import_module(name)
        logger.opt(colors=True).success(f"导入成功 <y>{short_name}</y>")
    except:
        logger.opt(colors=True).exception(f"导入失败 <y>{short_name}</y>")
