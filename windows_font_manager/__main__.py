import asyncio

from easyrip import log

from .font import font_data
from .global_val import WIN_FONT_PATHS
from .web import server


async def main():
    log.write_level = log.LogLevel.none
    log.init()

    await font_data.add_font_data_dir(*WIN_FONT_PATHS)
    await server.run()


def run():
    asyncio.run(main())


if __name__ == "__main__":
    run()
