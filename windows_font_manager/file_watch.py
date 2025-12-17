import asyncio
import json
from typing import override

from easyrip import log
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from .font import font_data
from .web.msg import process_msg, push_msg


class File_watch(FileSystemEventHandler):
    @override
    def on_any_event(self, event: FileSystemEvent) -> None:
        log.info(
            f'File watch: {event.event_type}: "{event.src_path}"{f' -> "{event.dest_path}"' if event.dest_path else ""}',
            is_format=False,
        )
        font_data.refresh_font_data_dict()
        asyncio.run(push_msg(asyncio.run(process_msg(json.dumps({"get_fonts": ""})))))


async def start_file_watch(*paths: str):
    observer = Observer()
    for path in paths:
        observer.schedule(File_watch(), path, recursive=True)
    observer.start()
    return observer
