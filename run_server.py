import subprocess
import time
import sys
import os

def main():
    print("==================================================================")
    print("    HH GOA 2026 — VOICE-ENABLED RAG PIPELINE (#RAGInGoa)")
    print("==================================================================")
    print("Starting FastAPI Backend on http://localhost:8000 ...")
    print("Starting React/Vite Frontend on http://localhost:3000 ...")

    root_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(root_dir, "frontend")

    # 1. Start FastAPI Backend
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=root_dir
    )

    # 2. Start Vite Frontend
    frontend_proc = subprocess.Popen(
        ["npx.cmd", "vite", "--port", "3000"],
        cwd=frontend_dir
    )

    print("\n[SUCCESS] Servers launched!")
    print("  Backend API:  http://localhost:8000/api/health")
    print("  API Docs:     http://localhost:8000/docs")
    print("  Web App UI:   http://localhost:3000")
    print("Press Ctrl+C to stop servers.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping processes...")
        backend_proc.terminate()
        frontend_proc.terminate()

if __name__ == "__main__":
    main()
