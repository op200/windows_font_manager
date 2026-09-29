import subprocess

from build_hook import run_pnpm

if __name__ == "__main__":
    run_pnpm()
    subprocess.run(["python", "-m", "build"], check=True)
