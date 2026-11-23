"""
Smart Launcher for Movie Analytics Dashboard
Run in VS Code terminal via: python run.py
"""

import sys
import os
import time
import socket
import subprocess

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(('127.0.0.1', port)) == 0

def free_port(port: int):
    """Attempts to kill stale processes occupying the target port on Windows."""
    try:
        cmd = f'netstat -ano | findstr LISTENING | findstr :{port}'
        output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
        for line in output.strip().splitlines():
            parts = line.split()
            if len(parts) >= 5:
                pid = parts[-1]
                print(f"[*] Port {port} was in use by PID {pid}. Terminating stale process...")
                subprocess.run(f'taskkill /F /PID {pid}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(1)
    except Exception:
        pass

def find_available_port(start_port: int = 8501) -> int:
    port = start_port
    while is_port_in_use(port):
        free_port(port)
        if not is_port_in_use(port):
            return port
        port += 1
    return port

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "app.py")
    python_exe = sys.executable

    target_port = find_available_port(8501)

    print("============================================================")
    print("   🎬 Movie Catalogue, Ratings & Revenue Dashboard         ")
    print("============================================================")
    print(f"[*] Python: {python_exe}")
    print(f"[*] Starting Streamlit on http://localhost:{target_port} ...")
    print("[*] Press Ctrl+C in this terminal to stop.")
    print("============================================================\n")

    cmd = [python_exe, "-m", "streamlit", "run", app_path, "--server.port", str(target_port)]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n[+] Dashboard stopped.")

if __name__ == "__main__":
    main()
