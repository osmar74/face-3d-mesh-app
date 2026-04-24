import subprocess
import sys
import os
import webbrowser
import time
import threading


BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8000
FRONTEND_PORT = 5500


def open_browser():
    time.sleep(3)
    webbrowser.open(f"http://127.0.0.1:{FRONTEND_PORT}/frontend/")


def run_backend():
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "backend.app.main:app",
        "--host", BACKEND_HOST,
        "--port", str(BACKEND_PORT),
        "--reload"
    ])


def run_frontend():
    subprocess.run([
        sys.executable, "-m", "http.server",
        str(FRONTEND_PORT)
    ])


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("=" * 55)
    print("  Face 3D Mesh App — Delaunay / PRNet / MediaPipe")
    print("=" * 55)
    print(f"  Backend : http://{BACKEND_HOST}:{BACKEND_PORT}")
    print(f"  Swagger : http://{BACKEND_HOST}:{BACKEND_PORT}/docs")
    print(f"  Frontend: http://127.0.0.1:{FRONTEND_PORT}/frontend/")
    print("  Modo    : desarrollo")
    print("  Detener : Ctrl+C")
    print("=" * 55)

    threading.Thread(target=open_browser, daemon=True).start()

    frontend_process = subprocess.Popen([
        sys.executable, "-m", "http.server",
        str(FRONTEND_PORT)
    ])

    try:
        run_backend()
    except KeyboardInterrupt:
        print("\nDeteniendo servidores...")
    finally:
        frontend_process.terminate()
        frontend_process.wait()


if __name__ == "__main__":
    main()