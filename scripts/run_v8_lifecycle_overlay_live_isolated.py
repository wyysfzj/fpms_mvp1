from __future__ import annotations

import json
import os
import socket
import subprocess
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


def main() -> int:
    backend = ROOT / "backend"
    frontend = ROOT / "frontend"
    playwright = ROOT / "FPMS_Automation_Skeleton_Pack/playwright_ts"
    with tempfile.TemporaryDirectory(prefix="fpms-row281-lifecycle-") as temp_name:
        temp = Path(temp_name)
        backend_port = _free_port()
        frontend_port = _free_port()
        origin = f"http://127.0.0.1:{frontend_port}"
        api_base = f"http://127.0.0.1:{backend_port}/api/v1"
        environment = {
            **os.environ,
            "FPMS_ENV": "test",
            "DATABASE_URL": f"sqlite:///{temp / 'live.db'}",
            "STORAGE_DIR": str(temp / "storage"),
            "CORS_ORIGINS": json.dumps([origin]),
            "NO_PROXY": "127.0.0.1,localhost",
            "no_proxy": "127.0.0.1,localhost",
        }
        subprocess.run(
            [backend / ".venv/bin/alembic", "upgrade", "head"],
            cwd=backend,
            env=environment,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            [backend / ".venv/bin/python", "scripts/seed_dev.py"],
            cwd=backend,
            env=environment,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        backend_log_path = temp / "backend.log"
        frontend_log_path = temp / "frontend.log"
        with (
            backend_log_path.open("w") as backend_log,
            frontend_log_path.open("w") as frontend_log,
        ):
            backend_process = subprocess.Popen(
                [
                    backend / ".venv/bin/python",
                    "-m",
                    "uvicorn",
                    "app.main:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(backend_port),
                ],
                cwd=backend,
                env=environment,
                stdout=backend_log,
                stderr=subprocess.STDOUT,
                text=True,
            )
            frontend_process = subprocess.Popen(
                [
                    frontend / "node_modules/.bin/vite",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(frontend_port),
                    "--strictPort",
                ],
                cwd=frontend,
                env={**environment, "VITE_API_BASE_URL": api_base},
                stdout=frontend_log,
                stderr=subprocess.STDOUT,
                text=True,
            )
            try:
                _wait_http(
                    backend_process,
                    f"http://127.0.0.1:{backend_port}/healthz",
                    backend_log_path,
                )
                _wait_http(frontend_process, origin, frontend_log_path)
                result = subprocess.run(
                    [
                        "npx",
                        "playwright",
                        "test",
                        "src/tests/v8-lifecycle-overlay-live.spec.ts",
                        "--workers=1",
                    ],
                    cwd=playwright,
                    env={
                        **environment,
                        "FPMS_BASE_URL": origin,
                        "FPMS_BACKEND_PYTHON": str(backend / ".venv/bin/python"),
                    },
                    check=False,
                )
                return result.returncode
            finally:
                _stop(frontend_process)
                _stop(backend_process)


if __name__ == "__main__":
    raise SystemExit(main())
