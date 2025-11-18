import os
import sys
import time
import ctypes
import subprocess

default_temp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_elevated_ps.txt")
# __temp_path = os.path.join(tempfile.gettempdir(), "run_elevated_ps.txt")
__tpl = f"powershell -NoProfile -ExecutionPolicy Bypass -Command {{cmd}}"
__si = subprocess.STARTUPINFO()
__si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
__si.wShowWindow = 0

def __escape_for_powershell_double_quoted(s: str) -> str:
    """
    Escape characters that would break a PowerShell double-quoted string:
      - backtick `  -> `` (double the backtick)
      - double-quote " -> `"
      - braces for Python .format()
    """
    s = s.replace("`", "``").replace('"', '`"')
    s = s.replace("{", "{{").replace("}", "}}")
    return s

def __elevated(cmd, temp_path):
    if "--_elevated" in sys.argv:
        # Get the command from sys.argv[2]
        if len(sys.argv) < 3:
            print("No command passed to elevated process!")
            sys.exit(1)
        cmd = sys.argv[2]

        _cmd = __escape_for_powershell_double_quoted(__tpl.format(cmd=cmd))
        r = subprocess.run(_cmd, capture_output=True, text=True, startupinfo=__si)

        # Write stdout, stderr, and timestamp to temp file
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(r.stdout + "\n----- STDERR -----\n" + r.stderr)
        sys.exit(0)
        

def run(cmd, timeout=30, temp_path = default_temp_path):
    """
    Runs the given PowerShell command as Administrator (hidden) and waits
    for the output file. Returns (stdout, stderr).
    """
    # elevated branch, should exit
    if "--_elevated" in sys.argv: __elevated(cmd, temp_path)

    # original branch
    # remove logging file
    try: os.remove(temp_path)
    except FileNotFoundError: pass

    # start elevated process by calling file again with flag
    args = f'"{os.path.abspath(sys.argv[0])}" --_elevated "{cmd}"'
    ret = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, args, None, 0
    )
    if ret <= 32:
        raise RuntimeError(f"Failed to elevate (ShellExecute returned {ret})")

    # wait for it to finish. elevated writes output to a file. parses
    start = time.time()
    while time.time() - start < timeout:
        if os.path.exists(temp_path):
            with open(temp_path, encoding="utf-8") as f:
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
        time.sleep(0.1)

    raise TimeoutError("Timed out waiting for elevated output")


__ps1_eps = "https://raw.githubusercontent.com/ElNosnhoj/scripts/refs/heads/main/.ps1/ElevatedPs.ps1"
__wtpl = f"$s=(Invoke-WebRequest -UseBasicParsing -Uri '{__ps1_eps}').Content; Invoke-Expression $s; ElevatedPs {{cmd}}"
def wrun(cmd, timeout=30):
    """
    Runs the given PowerShell command as Administrator (hidden) proxied by ps1 web script. 
    Returns (stdout, stderr)
    """
    # not sure why i couldn't do __tpl.format, but array seems to work
    wtpl = __wtpl.format(cmd=cmd)
    tpl = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", wtpl]
    proc = subprocess.run(tpl,capture_output=True,text=True,timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr

__all__ = ['run','wrun']

if __name__ == "__main__":
    # this command requires elevation. good for testing
    res = wrun("fsutil dirty query C:", 5)
    print(res)

