import asyncio
from ayaka import resource_download, get_file_hash

asyncio.run(resource_download("https://ghproxy.com/https://raw.githubusercontent.com/bridgeL/nonebot-plugin-ayaka-games/master/data/ayaka_games/文字税.txt", "test2.txt"))

print(get_file_hash("test.txt"))
print(get_file_hash("test2.txt"))
