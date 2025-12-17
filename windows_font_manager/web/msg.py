import itertools
import json
import weakref
from pathlib import Path
from typing import Any, Final, TypedDict

from easyrip import log
from easyrip.utils import type_match
from fastapi import WebSocket

from ..font import font_data
from ..global_val import VERSION

push_msg_ws_set: Final[weakref.WeakSet[WebSocket]] = weakref.WeakSet()
"""需要主动推送的 ws"""


async def push_msg(msg: str):
    """主动推送消息"""
    for ws in push_msg_ws_set:
        await ws.send_text(msg)


class Response_font_dict(TypedDict):
    pathname: str
    filename: str
    familys: list[str]
    font_type: str
    font_type_val: tuple[bool, bool]


class Response_font_info_dict(Response_font_dict):
    pass


class Response_dict(TypedDict):
    """None 表示不返回而不是返回为空"""

    info: dict
    execute: list[str]
    fonts: dict[str, list[Response_font_dict]] | None
    fonts_info: Response_font_info_dict | None


class Webui_msg_dict(TypedDict):
    get_fonts: str
    del_fonts: list[str]
    add_dirs: list[str]
    pop_dirs: list[str]
    get_font_info: Any  # TODO


async def process_msg(msg: str) -> str:
    """接收前端消息，返回后端消息"""
    res: Response_dict = {
        "info": {"version": VERSION},
        "execute": [],
        "fonts": None,
        "fonts_info": None,
    }

    data: Webui_msg_dict = json.loads(msg)

    def write_fonts() -> None:
        res["fonts"] = {
            dir_str: [
                {
                    "pathname": font.pathname,
                    "filename": Path(font.pathname).name,
                    "familys": list(font.familys),
                    "font_type": font.font_type.name,
                    "font_type_val": font.font_type.value,
                }
                for font in font_list
            ]
            for dir_str, font_list in font_data.font_data_dict.items()
        }

    for key, val in data.items():
        if key not in Webui_msg_dict.__annotations__:
            log.error("Unknown key: {}", key)
            continue
        res["execute"].append(key)
        match key:
            case "get_fonts":
                write_fonts()

            case "del_fonts":
                assert type_match(val, list[str])
                # 解除占用
                for font in itertools.chain.from_iterable(
                    font_data.font_data_dict.values()
                ):
                    if any(Path(del_font).samefile(font.pathname) for del_font in val):
                        font.font.close()
                        continue
                # 删除文件
                for pathname in val:
                    log.info("Delete font: {}", pathname)
                    try:
                        Path(pathname).unlink(True)
                    except PermissionError as e:
                        log.error("Delete faild: {}", e)
                # 刷新
                font_data.refresh_font_data_dict()
                write_fonts()

            case "add_dirs":
                assert type_match(val, list[str])
                font_data.add_font_data_dir(*val)
                write_fonts()

            case "pop_dirs":
                assert type_match(val, list[str])
                font_data.pop_font_data_dir(*val)
                write_fonts()

            case "get_font_info":
                pass
                # TODO
                # res["fonts_info"] = {}

    return json.dumps(res)
