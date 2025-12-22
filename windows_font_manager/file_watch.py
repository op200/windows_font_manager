import asyncio
import json
from pathlib import Path
from typing import TYPE_CHECKING, override

from easyrip import log
from easyrip.ripper.param import FONT_SUFFIX_SET
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.api import BaseObserver

if TYPE_CHECKING:
    from concurrent.futures import Future


class file_watch:
    observer: BaseObserver | None = None

    _main_loop: asyncio.AbstractEventLoop | None = None
    is_in_push_fonts_msg: bool = False
    is_will_push_fonts_msg: bool = False

    @classmethod
    def set_event_loop(cls, loop: asyncio.AbstractEventLoop) -> None:
        """设置主事件循环，需要在异步环境启动后调用"""
        cls._main_loop = loop

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

    class File_watch_event_handler(FileSystemEventHandler):
        @override
        def on_any_event(self, event: FileSystemEvent) -> None:
            src_path = Path(str(event.src_path))

            if src_path.suffix.lower() not in FONT_SUFFIX_SET:
                return

            log.info(
                f'File watch: {event.event_type}: "{event.src_path}"{f' -> "{event.dest_path}"' if event.dest_path else ""}',
                is_format=False,
            )

            # 线程安全的方式调用异步函数
            if not (file_watch._main_loop and file_watch._main_loop.is_running()):
                log.error(f"file_watch._main_loop = {file_watch._main_loop}")
                return
            future: Future = asyncio.run_coroutine_threadsafe(
                file_watch.push_fonts_msg(), file_watch._main_loop
            )
            # 可选：添加完成回调处理异常
            future.add_done_callback(
                lambda f: f.exception() if not f.cancelled() else None
            )

    file_watch_event_handler = File_watch_event_handler()

    @classmethod
    def stop(cls):
        if cls.observer is not None:
            cls.observer.stop()

    @classmethod
    def start(cls):
        if cls.observer is not None:
            try:
                cls.observer.start()
            except RuntimeError:
                pass

    @classmethod
    async def new_file_watch(cls, *paths: str) -> None:
        cls.stop()

        cls.observer = Observer()
        for path in paths:
            cls.observer.schedule(cls.file_watch_event_handler, path, recursive=True)

        cls.start()

        # 设置当前事件循环
        cls.set_event_loop(asyncio.get_running_loop())
