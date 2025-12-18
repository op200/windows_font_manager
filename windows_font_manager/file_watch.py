import asyncio
import json
from typing import override

from easyrip import log
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.api import BaseObserver


class file_watch:
    observer: BaseObserver | None = None

    is_in_push_fonts_msg: bool = False
    is_will_push_fonts_msg: bool = False

    @classmethod
    async def _push_fonts_msg_core(cls) -> None:
        from .font import font_data
        from .web.msg import process_msg, push_msg

        font_data.refresh_font_data_dict()
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

    class File_watch_event_handler(FileSystemEventHandler):
        @override
        def on_any_event(self, event: FileSystemEvent) -> None:
            log.info(
                f'File watch: {event.event_type}: "{event.src_path}"{f' -> "{event.dest_path}"' if event.dest_path else ""}',
                is_format=False,
            )
            asyncio.run(file_watch.push_fonts_msg())

    file_watch_event_handler = File_watch_event_handler()

    @classmethod
    async def new_file_watch(cls, *paths: str) -> None:
        if cls.observer is not None:
            cls.observer.stop()

        cls.observer = Observer()
        for path in paths:
            cls.observer.schedule(cls.file_watch_event_handler, path, recursive=True)
        cls.observer.start()
