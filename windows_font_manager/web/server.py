import importlib.resources as pkg_resources
import importlib.util
import itertools
import socket
from pathlib import Path
from typing import Literal, TypedDict

import uvicorn
from easyrip.easyrip_log import log
from easyrip.ripper.param import FONT_SUFFIX_SET
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ..font import font_data
from ..global_val import WIN_FONT_PATHS
from .msg import process_msg, push_msg_ws_set

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # 定时向客户端推送消息
    push_msg_ws_set.add(websocket)

    try:
        while True:
            msg: str = await websocket.receive_text()  # 接收客户端消息
            await websocket.send_text(await process_msg(msg))  # 发送响应给客户端
    except WebSocketDisconnect as e:
        log.info(f"Client disconnected {e.code}: {e.reason}")


@app.get("/gv/{key}")
async def gv(key: str):
    match key:
        case "WIN_FONT_PATHS":
            return WIN_FONT_PATHS
        case _:
            raise HTTPException(422, "Not an available key")


@app.get("/font/{url_path:path}")
async def font(url_path: str):
    path = Path(url_path)
    if path.suffix.lower() not in FONT_SUFFIX_SET:
        raise HTTPException(403, "Not a font")
    if all((not path.parent.samefile(s)) for s in font_data.font_data_dict):
        print(font_data.font_data_dict.keys(), path.parent)
        raise HTTPException(403, "Unloaded directory")
    return FileResponse(path)


class Font_info_req(BaseModel):
    pathname: str


class Font_info_res(TypedDict):
    pathname: str
    familys: set[str]
    font_type: Literal["Regular", "Bold", "Italic", "Bold_Italic"]
    created: int
    modified: int
    revision: float
    version: str | None
    is_variable: bool
    units_per_em: int
    glyph_count: int
    cmap_len: int
    copyright_notice: str | None
    unique_id: str | None
    full_name: str | None
    PostScript_name: str | None
    trademark: str | None
    manufacturer: str | None
    designer: str | None


@app.post("/font_info")
async def font_info(req: Font_info_req) -> Font_info_res:
    path = Path(req.pathname)
    if path.suffix.lower() not in FONT_SUFFIX_SET:
        raise HTTPException(403, "Not a font")
    for font in itertools.chain.from_iterable(font_data.font_data_dict.values()):
        if not path.samefile(font.pathname):
            continue
        return {
            "pathname": font.pathname,
            "familys": font.familys,
            "font_type": font.font_type.name,
            "created": font.font["head"].created,  # pyright: ignore[reportAttributeAccessIssue]
            "modified": font.font["head"].modified,
            "revision": font.font["head"].fontRevision,  # pyright: ignore[reportAttributeAccessIssue]
            "version": font.font["name"].getDebugName(5),
            "is_variable": "fvar" in font.font,
            "units_per_em": font.font["head"].unitsPerEm,  # pyright: ignore[reportAttributeAccessIssue]
            "glyph_count": font.font["maxp"].numGlyphs,
            "cmap_len": len(font.font.getBestCmap() or ()),
            "copyright_notice": font.font["name"].getDebugName(0),
            "unique_id": font.font["name"].getDebugName(3),
            "full_name": font.font["name"].getDebugName(4),
            "PostScript_name": font.font["name"].getDebugName(6),
            "trademark": font.font["name"].getDebugName(7),
            "manufacturer": font.font["name"].getDebugName(8),
            "designer": font.font["name"].getDebugName(9),
        }
    raise HTTPException(403, "Unloaded font file")


app.mount(
    "/",
    StaticFiles(
        directory=str(pkg_resources.files("windows_font_manager") / "static"), html=True
    ),
    name="root",
)


def find_available_port(start_port: int, max_port: int) -> int:
    for port in range(start_port, max_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("0.0.0.0", port))
                return port
        except OSError:
            continue
    raise Exception(
        f"There are no available ports within the range of {start_port}-{max_port}"
    )


async def run_server() -> None:
    host = "0.0.0.0"
    port = find_available_port(8423, 8999)

    import_string: bool = importlib.util.find_spec(__name__) is not None
    print(f"{import_string=}")

    config = uvicorn.Config(
        f"{__name__}:app" if import_string else app,
        host=host,
        port=port,
        reload=__debug__,
        log_level="info",
    )

    server = uvicorn.Server(config)
    print(f"Server: {host}:{port}")
    print(f"View: http://127.0.0.1:{port}")

    await server.serve()


async def run() -> None:
    try:
        await run_server()
    except KeyboardInterrupt:
        print("KeyboardInterrupt exit")
