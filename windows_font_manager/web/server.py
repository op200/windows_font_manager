import importlib.resources as pkg_resources
import socket

import uvicorn
from easyrip import log
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

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

    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        reload=True,
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
