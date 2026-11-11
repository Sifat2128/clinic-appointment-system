"""Automated E2E Test Runner
Starts backend and frontend servers, verifies health endpoints,
executes the Selenium test suite, and ensures graceful teardown.
"""
import os
import sys
import time
import shutil
import urllib.request
import subprocess

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_HEALTH_URL = "http://127.0.0.1:8000/health"
FRONTEND_URL = "http://127.0.0.1:5173"


def kill_proc_tree(proc):
    """Safely terminates a process and all its child processes on Windows or POSIX."""
    if not proc:
        return
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
        else:
            proc.terminate()
            proc.wait(timeout=3)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def wait_for_url(url: str, timeout: int = 30) -> bool:
    """Polls a URL until it responds with HTTP 200 or timeout expires."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(1)
    return False


def main():
    python_exe = sys.executable
    node_dir = r"C:\Users\ACER\AppData\Local\Microsoft\WinGet\Packages\OpenJS.NodeJS.LTS_Microsoft.Winget.Source_8wekyb3d8bbwe\node-v24.20.0-win-x64"
    env = os.environ.copy()
    if os.path.exists(node_dir):
        env["PATH"] = f"{node_dir};{env.get('PATH', '')}"

    npm_bin = shutil.which("npm", path=env["PATH"]) or "npm"
    is_win = sys.platform == "win32"

    print(f"[E2E Runner] Using Python: {python_exe}")
    print(f"[E2E Runner] Using NPM: {npm_bin}")

    # Remove local clinic.db for hermetic test run
    db_file = os.path.join(WORKSPACE_ROOT, "clinic.db")
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print("[E2E Runner] Cleaned existing clinic.db for hermetic E2E run.")
        except Exception as e:
            print(f"[E2E Runner] Note: could not delete clinic.db: {e}")

    backend_proc = None
    frontend_proc = None
    exit_code = 1

    try:
        print("[E2E Runner] 1. Starting FastAPI backend on http://127.0.0.1:8000 ...")
        backend_proc = subprocess.Popen(
            [python_exe, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=WORKSPACE_ROOT,
            env=env,
        )

        print("[E2E Runner] 2. Building frontend for production preview...")
        build_proc = subprocess.run(
            [npm_bin, "run", "build"],
            cwd=os.path.join(WORKSPACE_ROOT, "frontend"),
            env=env,
            shell=is_win,
            capture_output=True,
            text=True,
        )
        if build_proc.returncode != 0:
            print(f"[E2E Runner] Frontend build failed:\n{build_proc.stderr}")
            sys.exit(1)

        print("[E2E Runner] 3. Starting frontend preview server on http://127.0.0.1:5173 ...")
        frontend_proc = subprocess.Popen(
            [npm_bin, "run", "preview", "--", "--port", "5173", "--host", "127.0.0.1"],
            cwd=os.path.join(WORKSPACE_ROOT, "frontend"),
            env=env,
            shell=is_win,
        )

        print("[E2E Runner] Waiting for backend readiness...")
        if not wait_for_url(BACKEND_HEALTH_URL, timeout=30):
            raise RuntimeError("FastAPI backend failed to start within timeout.")
        print(" -> FastAPI backend is ready.")

        print("[E2E Runner] Waiting for frontend readiness...")
        if not wait_for_url(FRONTEND_URL, timeout=30):
            raise RuntimeError("Frontend server failed to start within timeout.")
        print(" -> Frontend server is ready.")

        print("[E2E Runner] 4. Executing Selenium E2E Suite with Headless Chrome...")
        pytest_proc = subprocess.run(
            [python_exe, "-m", "pytest", "e2e", "-v", "-s", "--ignore=e2e/runner.py"],
            cwd=WORKSPACE_ROOT,
            env=env,
        )
        exit_code = pytest_proc.returncode

    except Exception as e:
        print(f"[E2E Runner] Exception during execution: {e}")
        exit_code = 1
    finally:
        print("[E2E Runner] 5. Cleaning up processes...")
        kill_proc_tree(backend_proc)
        kill_proc_tree(frontend_proc)

    print(f"[E2E Runner] Finished with exit code: {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
