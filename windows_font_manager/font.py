import asyncio
import ctypes
from ctypes import wintypes
from pathlib import Path

from easyrip import log
from easyrip.ripper.sub_and_font.font import Font, load_fonts

from .global_val import WIN_FONT_PATHS


def get_windows_error_message(error_code: int) -> str:
    """
    根据Windows错误代码获取错误消息

    Args:
        error_code: Windows错误代码

    Returns:
        str: 错误描述

    """
    try:
        # 使用FormatMessage获取错误描述
        kernel32 = ctypes.WinDLL("kernel32.dll")
        kernel32.FormatMessageW.argtypes = [
            wintypes.DWORD,
            wintypes.LPVOID,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.LPWSTR,
            wintypes.DWORD,
            wintypes.LPVOID,
        ]
        kernel32.FormatMessageW.restype = wintypes.DWORD

        FORMAT_MESSAGE_FROM_SYSTEM = 0x00001000
        FORMAT_MESSAGE_IGNORE_INSERTS = 0x00000200

        buffer = ctypes.create_unicode_buffer(256)
        kernel32.FormatMessageW(
            FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
            None,
            error_code,
            0,
            buffer,
            ctypes.sizeof(buffer),
            None,
        )

        return buffer.value.strip()
    except Exception:
        return "Can not get detail"


def remove_win_font_resource(font_path: str) -> tuple[bool, str]:
    try:
        # 加载Windows DLL
        gdi32 = ctypes.WinDLL("gdi32.dll")
        user32 = ctypes.WinDLL("user32.dll")

        # 设置函数原型
        gdi32.RemoveFontResourceExW.argtypes = [
            wintypes.LPCWSTR,
            wintypes.DWORD,
            wintypes.LPVOID,
        ]
        gdi32.RemoveFontResourceExW.restype = wintypes.BOOL

        # 调用API移除字体
        result = gdi32.RemoveFontResourceExW(font_path, 0x10, None)

        if result:
            # 发送消息通知系统字体已变更
            user32.SendMessageW(0xFFFF, 0x001D, 0, 0)

            # 建议使用PostMessage进行广播，避免阻塞
            user32.PostMessageW(0xFFFF, 0x001D, 0, 0)

            return True, "Success"
        # 获取详细的错误信息
        error_code = ctypes.GetLastError()
        error_msg = get_windows_error_message(error_code)

    except Exception as e:
        return False, f"{remove_win_font_resource.__name__} error: {e}"

    return False, f"{remove_win_font_resource.__name__} faild {error_code}: {error_msg}"


def remove_font_reg(path: Path) -> tuple[bool, str]:
    import winreg

    hkey: int | None = None

    if path.parent.samefile(WIN_FONT_PATHS[0]):
        hkey = winreg.HKEY_LOCAL_MACHINE
    elif path.parent.samefile(WIN_FONT_PATHS[1]):
        hkey = winreg.HKEY_CURRENT_USER

    if hkey is None:
        return True, "Not a installation directory"

    try:
        key = winreg.OpenKey(
            hkey,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts",
            access=winreg.KEY_WRITE | winreg.KEY_READ,
        )
    except OSError as e:
        return False, f"faild to openkey: {e}"

    delete_keys: list[str] = []
    try:
        i = 0
        while True:
            name, value, _type = winreg.EnumValue(key, i)
            if path.name.lower() == Path(value).name.lower():
                delete_keys.append(name)
            i += 1
    except OSError:
        pass

    for name in delete_keys:
        try:
            winreg.DeleteValue(key, name)
        except OSError as e:
            return False, f"Failed to delete registry key {name}: {e}"

    return True, f"Successfully removed {len(delete_keys)} registry entries"


def remove_font(path: str | Path) -> tuple[bool, str]:
    path = Path(path)
    if not path.is_file():
        return False, "not a file"

    # 卸载资源
    remove_win_font_resource_res = remove_win_font_resource(str(path))
    if not remove_win_font_resource_res[0]:
        log.warning(remove_win_font_resource_res[1])

    # 删除文件
    try:
        path.unlink()
    except Exception as e:
        return False, f"paht.unlink faild: {e}"

    # 删除注册表
    try:
        remove_font_reg_res = remove_font_reg(path)
    except Exception as e:
        return False, f"{remove_font_reg.__name__} error: {e}"
    if not remove_font_reg_res[0]:
        return False, f"{remove_font_reg.__name__} faild: {remove_font_reg_res[1]}"

    return True, remove_font_reg_res[1]


class font_data:
    font_data_dict: dict[str, list[Font]] = {}
    """实时变化的监听目录及其结果"""

    @classmethod
    async def refresh_font_data_dict(cls):
        log.info(cls.refresh_font_data_dict.__name__)
        cls.font_data_dict = {
            d: await asyncio.to_thread(load_fonts, d) for d in cls.font_data_dict
        }

    @classmethod
    async def add_font_data_dir(cls, *dirs: str):
        from .file_watch import file_watch

        for d in dirs:
            cls.font_data_dict[d] = load_fonts(d)

        await file_watch.new_file_watch(*dirs)

    @classmethod
    def pop_font_data_dir(cls, *dirs: str):
        for d in dirs:
            try:
                cls.font_data_dict.pop(d)
            except KeyError as e:
                log.error(
                    "{} faild: {}",
                    cls.pop_font_data_dir.__name__,
                    e,
                )

    @classmethod
    def get_font_info(
        cls,
        pathname: str,
    ):  # TODO
        fonts = load_fonts(pathname)
