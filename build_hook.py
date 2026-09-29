import subprocess
from pathlib import Path

from setuptools.command.build import build  # pyright: ignore[reportMissingModuleSource]

DIR = "windows-font-manager-webui"
PNPM_HEAD = ["pnpm", "--dir", f"./{DIR}"]


def run_pnpm() -> None:
    for param in (
        ["i", "--frozen-lockfile"],
        ["build-only"],  # TODO: vue-tsc 不支持 TS7，支持后改为 build
    ):
        cmd: list[str] = PNPM_HEAD + param
        print(f"run: {cmd}")
        subprocess.run(cmd, shell=True, check=True)


class Build(build):
    def run(self) -> None:
        if not Path(DIR).is_dir():
            print(f'The dir "{DIR}" not found, do not run pnpm')
            return

        run_pnpm()

        super().run()
