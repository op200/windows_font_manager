import os

VERSION = "0.1.2"

WIN_FONT_PATHS: tuple[str, ...] = (
    os.path.join(os.environ["SYSTEMROOT"], "Fonts"),
    os.path.join(os.environ["LOCALAPPDATA"], "Microsoft/Windows/Fonts"),
)
