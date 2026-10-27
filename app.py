"""
FinTrack AI - Unified Application Launcher
Run both FastAPI Backend and Vite React Frontend concurrently.

Usage:
    python app.py                # Runs both backend and frontend, opens browser
    python app.py --backend      # Runs only backend
    python app.py --frontend     # Runs only frontend
    python app.py --no-browser   # Do not auto-launch browser
"""

import sys
import os
import subprocess
import time
import argparse
import webbrowser
import socket
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def main():
    parser = argparse.ArgumentParser(description="FinTrack AI Unified Runner")
    parser.add_argument("--backend", action="store_true", help="Start only backend")
    parser.add_argument("--frontend", action="store_true", help="Start only frontend")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")
    parser.add_argument("--host", default="127.0.0.1", help="Backend host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Backend port (default: 8000)")
    parser.add_argument("--frontend-port", type=int, default=5173, help="Frontend port (default: 5173)")
    args = parser.parse_args()

    run_backend = True
    run_frontend = True
    if args.backend and not args.frontend:
        run_frontend = False
    elif args.frontend and not args.backend:
        run_backend = False

    processes = []

    print("=" * 65)
    print("  [FinTrack AI] - Intelligent Expense & Finance Predictor")
    print("=" * 65)

    try:
        # Start Backend
        if run_backend:
            if is_port_in_use(args.port, args.host):
                print(f"[!] Warning: Port {args.port} is already in use. Backend may already be running.")
            else:
                print(f"[*] Starting FastAPI Backend on http://{args.host}:{args.port} ...")
                backend_cmd = [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "app.main:app",
                    "--host",
                    args.host,
                    "--port",
                    str(args.port),
                    "--reload"
                ]
                backend_proc = subprocess.Popen(
                    backend_cmd,
                    cwd=str(BACKEND_DIR)
                )
                processes.append(("Backend", backend_proc))

        # Start Frontend
        if run_frontend:
            npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
            if is_port_in_use(args.frontend_port):
                print(f"[!] Warning: Port {args.frontend_port} is already in use. Frontend may already be running.")
            else:
                print(f"[*] Starting React Vite Frontend on http://localhost:{args.frontend_port} ...")
                frontend_proc = subprocess.Popen(
                    [npm_cmd, "run", "dev"],
                    cwd=str(FRONTEND_DIR)
                )
                processes.append(("Frontend", frontend_proc))

        print("\n" + "-" * 65)
        if run_frontend:
            print(f"  -> Web Application:   http://localhost:{args.frontend_port}")
        if run_backend:
            print(f"  -> Backend API:       http://{args.host}:{args.port}")
            print(f"  -> Swagger Docs:      http://{args.host}:{args.port}/docs")
            print(f"  -> Health Check:      http://{args.host}:{args.port}/health")
        print("-" * 65)
        print("  Press Ctrl+C to stop all servers cleanly.\n")

        # Open browser if requested
        if run_frontend and not args.no_browser:
            time.sleep(1.5)
            webbrowser.open(f"http://localhost:{args.frontend_port}")

        # Keep parent alive and monitor child processes
        while True:
            time.sleep(1)
            for name, proc in processes:
                poll = proc.poll()
                if poll is not None:
                    print(f"[-] {name} stopped unexpectedly with code {poll}")
                    return poll

    except KeyboardInterrupt:
        print("\n[*] Shutting down servers gracefully...")
    finally:
        for name, proc in processes:
            if proc.poll() is None:
                print(f"[*] Terminating {name}...")
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
        print("[OK] All processes stopped.")


if __name__ == "__main__":
    main()
