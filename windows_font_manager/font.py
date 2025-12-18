from easyrip import log
from easyrip.ripper.sub_and_font.font import Font, load_fonts


class font_data:
    font_data_dict: dict[str, list[Font]] = {}
    """实时变化的监听目录及其结果"""

    @classmethod
    def refresh_font_data_dict(cls):
        cls.font_data_dict = {d: load_fonts(d) for d in cls.font_data_dict}

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
