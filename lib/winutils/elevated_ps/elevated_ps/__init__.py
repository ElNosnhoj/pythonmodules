import os, sys, time, ctypes, subprocess, tempfile

__temp_path = os.path.join(tempfile.gettempdir(), "run_elevated_ps.txt")
def run(cmd, timeout=30):
    """
    Runs the given PowerShell command as Administrator (hidden) and waits
    for the output file. Returns the combined stdout+stderr text.
    """
    # If this is the elevated run, execute and write the output
    if "--_elevated" in sys.argv:
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0
        _cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd]
        r = subprocess.run(_cmd, capture_output=True, text=True, startupinfo=si)
        with open(__temp_path, "w", encoding="utf-8") as f:
            f.write(r.stdout + "\n----- STDERR -----\n" + r.stderr)
        sys.exit(0)

    # Parent process: remove old file, elevate, wait for results
    try: os.remove(__temp_path)
    except FileNotFoundError: pass

    args = f'"{os.path.abspath(sys.argv[0])}" --_elevated'
    ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, args, None, 0)
    if ret <= 32:
        raise RuntimeError(f"Failed to elevate (ShellExecute returned {ret})")

    start = time.time()
    while time.time() - start < timeout:
        if os.path.exists(__temp_path):
            with open(__temp_path, encoding="utf-8") as f:
                # return f.read()
                content = f.read()
            if "----- STDERR -----" in content:
                out, err = content.split("----- STDERR -----", 1)
                out = out.strip()
                err = err.strip()
            else:
                out, err = content, ""
            return out, err
        time.sleep(0.2)
    raise TimeoutError("Timed out waiting for elevated output")


__all__ = ["run"]


if __name__ == "__main__":
    cmd = f"""echo 'This is run from elevated ps1'"""
    out, err = run(cmd)
    print(out)