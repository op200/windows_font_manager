import os
from pathlib import Path

from setuptools.command.build import build

DIR = "windows-font-manager-webui"
PNPM_HEAD = f"pnpm --dir ./{DIR}"


def run_pnpm() -> None:
    for param in (
        "i --frozen-lockfile",
        "build",
    ):
        cmd = f"{PNPM_HEAD} {param}"
        print(f"run: {cmd}")
        if os.system(cmd):
            raise RuntimeError(f"{cmd} error")


class Build(build):
    def run(self) -> None:
        if not Path(DIR).is_dir():
            print(f'The dir "{DIR}" not found, do not run pnpm')
            return

        run_pnpm()

        super().run()
