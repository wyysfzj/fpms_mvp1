from __future__ import annotations

import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _free_port() -> int:
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        return int(server.getsockname()[1])


def _wait_http(process: subprocess.Popen[str], url: str, log_path: Path) -> None:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for _ in range(160):
        if process.poll() is not None:
            tail = log_path.read_text(errors="replace")[-4000:]
            raise RuntimeError(f"child exited rc={process.returncode}: {tail}")
        try:
            with opener.open(url, timeout=0.5) as response:
                if response.status < 500:
                    return
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            time.sleep(0.25)
    raise RuntimeError(
        f"readiness timeout: {log_path.read_text(errors='replace')[-4000:]}"
    )


def _stop(process: subprocess.Popen[str]) -> None:
    if process.poll() is None:
        process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def main(specs: list[str]) -> int:
    if not specs or any(
        not spec.startswith("src/tests/") or not spec.endswith(".spec.ts")
        for spec in specs
    ):
        raise ValueError("pass one or more exact src/tests/*.spec.ts paths")
    frontend = ROOT / "frontend"
    playwright = ROOT / "FPMS_Automation_Skeleton_Pack/playwright_ts"
    missing = [spec for spec in specs if not (playwright / spec).is_file()]
    if missing:
        raise FileNotFoundError(f"missing Playwright specs: {missing}")

    with tempfile.TemporaryDirectory(prefix="fpms-row281-mock-") as temp_name:
        log_path = Path(temp_name) / "frontend.log"
        port = _free_port()
        origin = f"http://127.0.0.1:{port}"
        environment = {
            **os.environ,
            "NO_PROXY": "127.0.0.1,localhost",
            "no_proxy": "127.0.0.1,localhost",
        }
        with log_path.open("w") as log:
            process = subprocess.Popen(
                [
                    frontend / "node_modules/.bin/vite",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(port),
                    "--strictPort",
                ],
                cwd=frontend,
                env=environment,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
            )
            try:
                _wait_http(process, origin, log_path)
                result = subprocess.run(
                    ["npx", "playwright", "test", *specs, "--workers=1"],
                    cwd=playwright,
                    env={**environment, "FPMS_BASE_URL": origin},
                    check=False,
                )
                return result.returncode
            finally:
                _stop(process)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
