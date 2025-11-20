"""
Fast async IP scanner with a synchronous API.

Usage:
    scanned_ips = get_ips()            # default 192.168.137.2-254, 100ms timeout
    scanned_ips = get_ips(base="10.0.0.", start=1, end=254, timeout=0.05, concurrency=200)
"""

import asyncio
import aioping
import time
from typing import List, Optional

# Default scan parameters
DEFAULT_BASE = "192.168.5."
DEFAULT_START = 2
DEFAULT_END = 50
DEFAULT_TIMEOUT = 0.1     # seconds (100 ms)
DEFAULT_CONCURRENCY = 300

# Internal async scanner
async def _scan_async(base: str, start: int, end: int, timeout: float, concurrency: int) -> List[str]:
    sem = asyncio.Semaphore(concurrency)

    async def ping_one(ip: str) -> Optional[str]:
        async with sem:
            try:
                # aioping.ping raises TimeoutError on no reply
                await aioping.ping(ip, timeout=timeout)
                return ip
            except TimeoutError:
                return None
            except PermissionError:
                # Bubble up permission errors to caller by re-raising
                raise
            except Exception:
                # Ignore other transient errors (you can log if desired)
                return None

    tasks = [asyncio.create_task(ping_one(f"{base}{i}")) for i in range(start, end + 1)]
    results = await asyncio.gather(*tasks)
    # Filter only the alive IP strings
    alive = [r for r in results if isinstance(r, str)]
    return alive

# Public synchronous API
def get_ips(
    base: str = DEFAULT_BASE,
    start: int = DEFAULT_START,
    end: int = DEFAULT_END,
    timeout: float = DEFAULT_TIMEOUT,
    concurrency: int = DEFAULT_CONCURRENCY,
    show_timing: bool = False,
) -> List[str]:
    """
    Scan IPs synchronously and return a list of alive IP strings.

    Example:
        ips = get_ips()
    """
    # Basic parameter validation
    if start < 1 or end > 254 or start > end:
        raise ValueError("start/end must be 1..254 and start <= end")
    if concurrency < 1:
        raise ValueError("concurrency must be >= 1")

    start_time = time.perf_counter()
    try:
        alive = asyncio.run(_scan_async(base, start, end, timeout, concurrency))
    except PermissionError as e:
        # Common on Linux if not running with raw socket permissions
        raise PermissionError(
            "Permission error: raw sockets required. Run as root/Administrator or give cap_net_raw to the Python binary."
        ) from e
    elapsed = time.perf_counter() - start_time
    if show_timing:
        print(f"Scan finished in {elapsed:.3f}s. Alive: {len(alive)}")
    return alive

__all__ = ["get_ips"]

# If run as script, demonstrate usage and print results
if __name__ == "__main__":
    try:
        ips = get_ips()
        print(ips)
    except PermissionError as e:
        print(e)
        print("On Linux you can grant raw-socket capability instead of running as root:")
        print("  sudo setcap cap_net_raw+ep $(which python3)")
        print('  sudo setcap cap_net_raw+ep "$(readlink -f $(which python3))"')
