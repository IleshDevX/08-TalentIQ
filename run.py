"""
TalentIQ — Single-Command Launcher
Starts both FastAPI backend (port 8000) and Streamlit frontend (port 8501).

Usage:
    python run.py          # Start both API + Streamlit
    python run.py --api    # Start only the API
    python run.py --ui     # Start only Streamlit

Press Ctrl+C to stop all services.
"""

import os
import sys
import signal
import subprocess
import time

ROOT = os.path.dirname(os.path.abspath(__file__))

# Detect python executable within the venv
if sys.platform == "win32":
    PYTHON = os.path.join(ROOT, "venv", "Scripts", "python.exe")
else:
    PYTHON = os.path.join(ROOT, "venv", "bin", "python")

if not os.path.exists(PYTHON):
    PYTHON = sys.executable  # fallback to current interpreter

processes: list[subprocess.Popen] = []


def start_api() -> subprocess.Popen:
    """Launch FastAPI via uvicorn."""
    cmd = [PYTHON, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]
    print(f"\n🚀 Starting TalentIQ API on http://127.0.0.1:8000")
    proc = subprocess.Popen(cmd, cwd=ROOT)
    processes.append(proc)
    return proc


def start_ui() -> subprocess.Popen:
    """Launch Streamlit dashboard."""
    cmd = [PYTHON, "-m", "streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.headless", "true"]
    print(f"🖥️  Starting TalentIQ Dashboard on http://127.0.0.1:8501")
    proc = subprocess.Popen(cmd, cwd=ROOT)
    processes.append(proc)
    return proc


def shutdown(*_args):
    """Terminate all child processes."""
    print("\n\n🛑 Shutting down TalentIQ...")
    for proc in processes:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
    print("👋 All services stopped.")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    mode = sys.argv[1] if len(sys.argv) > 1 else "--all"

    print("=" * 50)
    print("  TalentIQ — AI-Powered Career Intelligence")
    print("=" * 50)

    if mode in ("--api", "--all"):
        start_api()
    if mode in ("--ui", "--all"):
        time.sleep(2)  # let API start first
        start_ui()

    print("\n✅ TalentIQ is running. Press Ctrl+C to stop.\n")

    # Wait for any process to exit
    try:
        while True:
            for proc in processes:
                if proc.poll() is not None:
                    print(f"⚠️  Process (PID {proc.pid}) exited with code {proc.returncode}")
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown()


if __name__ == "__main__":
    main()
