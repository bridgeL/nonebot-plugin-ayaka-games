# 导入全部插件
from pathlib import Path
from ayaka.ayaka import load_plugins
load_plugins(Path(__file__).parent, "ayaka_games")
