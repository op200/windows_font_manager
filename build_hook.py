import os

from setuptools.command.build import build

PNPM_HEAD = "pnpm --dir ./windows-font-manager-webui"


class Build(build):
    def run(self):
        for cmd in (f"{PNPM_HEAD} i", f"{PNPM_HEAD} build"):
            print(f"run: {cmd}")
            if os.system(cmd):
                raise RuntimeError(f"{cmd} error")

        super().run()
