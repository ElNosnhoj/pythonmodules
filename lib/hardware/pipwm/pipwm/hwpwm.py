import time
import os
from unittest.mock import patch

__base = "/sys/class/pwm/pwmchip0"
 
def __check_sysfs_available(path=__base):
    """
    Check that the required sysfs path exists, is a directory, and is accessible.
    Raises RuntimeError if anything is wrong.
    """
    if not os.path.exists(path):
        raise RuntimeError(f"Required sysfs path not found: {path}")
    if not os.path.isdir(path):
        raise RuntimeError(f"Expected directory but found something else at {path}")
    if not os.access(path, os.R_OK | os.X_OK):
        raise RuntimeError(f"Insufficient permissions to access {path}")


class HWPWM:
    """
    Hardware PWM wrapper for Raspberry Pi sysfs interface.
    Provides properties for export, enable, period, frequency, and duty cycle.
    """
    BASE: str = globals()['__base']
    EXPORT: str = f"{BASE}/export"
    UNEXPORT: str = f"{BASE}/unexport"

    def __init__(self, ch:int, chip:int=0):
        """
        Initialize a PWM channel.
        :param ch: PWM channel number
        :param chip: PWM chip
        """
        self.ch = ch
        self.chip = 0 
        self.base = f"{HWPWM.BASE}/pwm{ch}"

    def get_export(self) -> bool:
        """Return True if PWM channel is exported, False otherwise."""
        return os.path.exists(self.base)
    def set_export(self, state:bool) -> None:
        """Export or unexport the PWM channel."""
        with open(HWPWM.EXPORT if state else HWPWM.UNEXPORT, "w") as f:
            f.write(str(self.ch))
        time.sleep(0.01)
    export = property(get_export, set_export)

    def get_enable(self) -> bool:
        """Return True if PWM is enabled, False otherwise."""
        if not self.export: raise RuntimeError(f"PWM channel {self.ch} not exported")
        with open(f"{self.base}/enable", "r") as f:
            return f.read().strip() == "1"
    def set_enable(self, state:bool) -> None: 
        """Enable or disable the PWM output."""
        if not self.export: raise RuntimeError(f"PWM channel {self.ch} not exported")
        with open(f"{self.base}/enable", "w") as f:
            f.write("1" if state else "0")
    enable = property(get_enable, set_enable)

    def get_period(self) -> int:
        """Return PWM period in nanoseconds."""
        if not self.export: raise RuntimeError(f"PWM channel {self.ch} not exported")
        with open(f"{self.base}/period", 'r') as f:
            ns = int(f.read().strip())
        return ns
    def set_period(self, per:int) -> None:
        """Set PWM period in nanoseconds."""
        if not self.export: raise RuntimeError(f"PWM channel {self.ch} not exported")
        assert per > 0, f"Cannot set period <= 0: {per}"
        with open(f"{self.base}/period", 'w') as f:
            f.write(str(per))
    period = property(get_period, set_period)

    def get_hz(self) -> int:
        """Return PWM frequency in Hz."""
        if not self.export: raise RuntimeError(f"PWM channel {self.ch} not exported")
        ns = self.get_period()
        return int(1_000_000_000 / ns)
    def set_hz(self, hz:int) -> None:
        """Set PWM frequency in Hz."""
        if not self.export: raise RuntimeError(f"PWM channel {self.ch} not exported")
        assert hz > 0, f"Cannot set Hz <= 0: {hz}"
        ns = int(1_000_000_000 / hz)
        self.set_period(ns)
    hz = property(get_hz, set_hz)

    def __get_dc(self) -> int:
        """Return duty cycle in nanoseconds (internal)."""
        if not self.export: raise RuntimeError(f"PWM channel {self.ch} not exported")
        with open(f"{self.base}/duty_cycle", 'r') as f:
            ns = int(f.read().strip())
        return ns
    def __set_dc(self, duty_ns:int) -> None:
        """Set duty cycle in nanoseconds (internal)."""
        if not self.export: raise RuntimeError(f"PWM channel {self.ch} not exported")
        assert 0 <= duty_ns <= self.get_period(), f"Duty cycle out of range: {duty_ns}"
        with open(f"{self.base}/duty_cycle", 'w') as f:
            f.write(str(duty_ns))
    def get_dc(self) -> int:
        """Return duty cycle as a percentage [0-100]."""
        if not self.export: raise RuntimeError(f"PWM channel {self.ch} not exported")
        return self.__get_dc() / self.get_period() * 100
    def set_dc(self, dc:int) -> None:
        """Set duty cycle as a percentage [0-100]."""
        if not self.export: raise RuntimeError(f"PWM channel {self.ch} not exported")
        if dc < 0: dc = 0
        elif dc > 100: dc = 100
        period_ns = self.get_period()
        duty_ns = int(period_ns * dc / 100)
        self.__set_dc(duty_ns)
    dc = property(get_dc, set_dc)

    def start(self, hz, dc) -> None:
        """
        Start the PWM output with the given frequency and duty cycle.
        Automatically exports the channel if necessary.
        """
        if not self.export:
            self.export = True
        self.hz = hz
        self.dc = dc
        self.enable = 1
    
    def stop(self, unexport:bool=False) -> None:
        """
        Stop the PWM output.
        Optionally unexport the channel.
        """
        if self.enable:
            self.enable = False
        if unexport:
            self.export = False

    @classmethod
    def CLEANUP(cls) -> None:
        """
        Disable all PWM channels and unexport them.
        Useful for cleanup at program exit.
        """
        for i in range(4):
            base = f"{cls.BASE}/pwm{i}"
            enable_path = f"{base}/enable"
            if os.path.exists(enable_path):
                try:
                    with open(enable_path, "w") as f:
                        f.write("0")
                except Exception:
                    pass
            if os.path.exists(base):
                try:
                    with open(cls.UNEXPORT, "w") as f:
                        f.write(str(i))
                except Exception:
                    pass

def _MOCK()-> None:
    """
    Replace HWPWM and sysfs checks with a mock version for testing without hardware.
    """
    class __MOCK_HWPWM(HWPWM):
        def __init__(self, ch, chip = 0):
            super().__init__(ch, chip)
            self.__ex = False
            self.__en = False
            self.__period = -1
            self.__hz = -1
            self.__dc = -1
        
        def get_export(self): return self.__ex
        def set_export(self, state:bool): self.__ex = bool(state)
        export = property(get_export, set_export)

        def get_enable(self): return self.__en
        def set_enable(self, state:bool): 
            if not self.__ex: raise RuntimeError("Cannot enable before export")
            self.__en = bool(state)
        enable = property(get_enable, set_enable)

        def get_period(self):
            return self.__period

        def set_period(self, per:int):
            if not self.__ex: raise RuntimeError(f"PWM channel {self.ch} not exported")
            if per <= 0:
                raise ValueError("Period must be > 0")
            self.__period = per
            # automatically update hz to stay consistent
            self.__hz = int(1_000_000_000 / per)
        period = property(get_period, set_period)

        def get_hz(self): return self.__hz
        def set_hz(self, hz:int): 
            if not self.__ex: raise RuntimeError(f"PWM channel {self.ch} not exported")
            if hz <= 0: raise ValueError("Hz must be > 0")
            self.__hz = hz
            self.__period = int(1_000_000_000 / hz)
        hz = property(get_hz, set_hz)

        def get_dc(self): return self.__dc
        def set_dc(self, dc:int): 
            if dc < 0: dc = 0
            elif dc > 100: dc = 100
            self.__dc = dc

        dc = property(get_dc, set_dc)



    patch(f'{__name__}.__check_sysfs_available',return_value=None).start()
    patch(f'{__name__}.HWPWM', new=__MOCK_HWPWM).start()

if os.getenv("MOCK", "0") != "0": _MOCK()
try:
    __check_sysfs_available()
except Exception as e:
    raise ImportError(f"Sysfs interface check failed: {e}")

if __name__ == "__main__":
    pwm = HWPWM(2)
    pwm.start(25000, 100)

    dc = 100
    while dc>0:
        time.sleep(0.3)
        dc-=10
        pwm.dc = dc

    while dc<100:
        time.sleep(0.3)
        dc+=10
        pwm.dc = dc

    pwm.stop(True)
