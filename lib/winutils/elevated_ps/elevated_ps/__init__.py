import os
import sys
import time
import ctypes
import subprocess

__temp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_elevated_ps.txt")
# __temp_path = os.path.join(tempfile.gettempdir(), "run_elevated_ps.txt")
def run(cmd, timeout=30):
    """
    Runs the given PowerShell command as Administrator (hidden) and waits
    for the output file. Returns (stdout, stderr).
    """

    # Elevated branch
    if "--_elevated" in sys.argv:
        # Get the command from sys.argv[2]
        if len(sys.argv) < 3:
            print("No command passed to elevated process!")
            sys.exit(1)
        cmd = sys.argv[2]

        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0

        _cmd = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            cmd,
        ]
        r = subprocess.run(_cmd, capture_output=True, text=True, startupinfo=si)

        # Write stdout, stderr, and timestamp to temp file
        with open(__temp_path, "w", encoding="utf-8") as f:
            # f.write(f"cmd: {cmd}\n")
            # f.write(f"Timestamp: {time.time()}\n")
            f.write(r.stdout + "\n----- STDERR -----\n" + r.stderr)
        sys.exit(0)

    # Parent branch
    try:
        os.remove(__temp_path)
    except FileNotFoundError:
        pass

    # Pass the command as an argument to the elevated process
    args = f'"{os.path.abspath(sys.argv[0])}" --_elevated "{cmd}"'
    ret = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, args, None, 0
    )
    if ret <= 32:
        raise RuntimeError(f"Failed to elevate (ShellExecute returned {ret})")

    # Wait for temp file to appear
    start = time.time()
    while time.time() - start < timeout:
        if os.path.exists(__temp_path):
            with open(__temp_path, encoding="utf-8") as f:
                content = f.read()
            if "----- STDERR -----" in content:
                out, err = content.split("----- STDERR -----", 1)
                out = out.strip()
                err = err.strip()
            else:
                out, err = content, ""
            try:
                # os.remove(__temp_path)
                pass
            except FileNotFoundError:
                pass
            return out, err
        time.sleep(0.2)

    raise TimeoutError("Timed out waiting for elevated output")

