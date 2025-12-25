import asyncio
import itertools
import json
import weakref
from functools import cache
from pathlib import Path
from typing import Any, Final, TypedDict

from easyrip import log
from easyrip.easyrip_web.third_party_api import github
from easyrip.utils import type_match
from fastapi import WebSocket

from ..file_watch import file_watch
from ..font import font_data, remove_font
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


class Response_info(TypedDict):
    version: str
    latest_release_ver: str | None


class Response_dict(TypedDict):
    """None 表示不返回而不是返回为空"""

    info: Response_info
    execute: list[str]
    fonts: dict[str, list[Response_font_dict]] | None
    fonts_info: Response_font_info_dict | None


class Webui_msg_dict(TypedDict):
    wait_ms: int
    get_fonts: str
    del_fonts: list[str]
    add_dirs: list[str]
    pop_dirs: list[str]
    get_font_info: Any  # TODO


@cache
def _get_github_latest_release_ver(release_api_url: str) -> str | None:
    return github.get_latest_release_ver(release_api_url)


async def get_github_latest_release_ver(release_api_url: str) -> str | None:
    return _get_github_latest_release_ver(release_api_url)


async def process_msg(msg: str) -> str:
    """接收前端消息，返回后端消息"""
    res: Response_dict = {
        "info": {
            "version": VERSION,
            "latest_release_ver": await get_github_latest_release_ver(
                "https://api.github.com/repos/op200/windows_font_manager/releases/latest"
            ),
        },
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
            case "wait_ms":
                assert isinstance(val, int)

                if val >= 0:
                    log.info("Wait {}ms", val)
                    await asyncio.sleep(val / 1000)
                else:
                    log.warning("The '{}: {}' is illegal", key, val)

            case "get_fonts":
                write_fonts()

            case "del_fonts":
                assert type_match(val, list[str])
                # 解除占用
                for font in itertools.chain.from_iterable(
                    font_data.font_data_dict.values()
                ):
                    if any(Path(del_font).samefile(font.pathname) for del_font in val):
                        # if any(map(Path(font.pathname).samefile, val)):
                        font.font.close()
                        continue
                file_watch.stop()
                # 删除文件
                for pathname in val:
                    log.info("Delete font: {}", pathname)
                    try:
                        remove_res = remove_font(pathname)
                        if not remove_res[0]:
                            raise Exception(remove_res[1])
                    except Exception as e:
                        log.error("Delete font faild: {}", e)
                    else:
                        log.info("Delete font success: {}", remove_res[1])
                # 刷新
                await font_data.refresh_font_data_dict()
                file_watch.start()
                write_fonts()

            case "add_dirs":
                assert type_match(val, list[str])
                await font_data.add_font_data_dir(*val)
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
