import asyncio
import json
from pathlib import Path

from easyrip.easyrip_log import log
from easyrip.ripper.param import FONT_SUFFIX_SET
from watchfiles import awatch


class file_watch:
    watch_task: asyncio.Task | None = None

    is_in_push_fonts_msg: bool = False
    is_will_push_fonts_msg: bool = False

    @classmethod
    async def _push_fonts_msg_core(cls) -> None:
        from .font import font_data
        from .web.msg import process_msg, push_msg

        await font_data.refresh_font_data_dict()
        await push_msg(await process_msg(json.dumps({"get_fonts": ""})))

    @classmethod
    async def push_fonts_msg(cls) -> None:
        if cls.is_in_push_fonts_msg:
            cls.is_will_push_fonts_msg = True
            return

        try:
            cls.is_in_push_fonts_msg = True
            await cls._push_fonts_msg_core()
        finally:
            cls.is_in_push_fonts_msg = False

        if cls.is_will_push_fonts_msg:
            cls.is_will_push_fonts_msg = False
            await cls.push_fonts_msg()

    @classmethod
    async def _watch(cls, *paths: str) -> None:
        async for changes in awatch(*paths, recursive=True):
            for change, path in changes:
                src_path = Path(path)

                if src_path.suffix.lower() not in FONT_SUFFIX_SET:
                    continue

                log.info(
                    f'File watch: {change.name}: "{path}"',
                    is_format=False,
                )

            if any(Path(path).suffix.lower() in FONT_SUFFIX_SET for _, path in changes):
                await cls.push_fonts_msg()

    @classmethod
    def stop(cls) -> None:
        if cls.watch_task is not None:
            cls.watch_task.cancel()
            cls.watch_task = None

    @classmethod
    async def new_file_watch(cls, *paths: str) -> None:
        cls.stop()
        cls.watch_task = asyncio.create_task(cls._watch(*paths))
