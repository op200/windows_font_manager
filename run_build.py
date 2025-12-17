import os

from build_hook import run_pnpm

if __name__ == "__main__":
    run_pnpm()
    os.system("python -m build")
