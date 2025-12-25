import os
from pathlib import Path

VERSION = "0.3.2"

WIN_FONT_PATHS: tuple[str, ...] = tuple(
    path if Path(path).is_dir() else ""
    for path in (
        os.path.join(os.environ.get("SYSTEMROOT", ""), "Fonts"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft/Windows/Fonts"),
    )
)
"""
* [0] = windows font
* [1] = user font
"""
