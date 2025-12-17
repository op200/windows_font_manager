import asyncio
import os

from easyrip import log

from .file_watch import start_file_watch
from .font import font_data
from .web import server


async def main():
    WIN_FONT_PATHS: tuple[str, ...] = (
        os.path.join(os.environ["SYSTEMROOT"], "Fonts"),
        os.path.join(os.environ["LOCALAPPDATA"], "Microsoft/Windows/Fonts"),
    )

    log.write_level = log.LogLevel.none
    log.init()

    font_data.add_font_data_dir(*WIN_FONT_PATHS)
    # TODO 动态添加的path也要监听
    await asyncio.gather(server.run(), start_file_watch(*WIN_FONT_PATHS))


def run():
    asyncio.run(main())


if __name__ == "__main__":
    run()
