#===================================================================
# pigpiod
# desc: control rpi5 gpio with mock for use with testing
#       uses gpiod and not sysfs
#===================================================================
import asyncio
import threading
from typing import Literal, Callable, Optional, List

# Try importing real gpiod; fallback to mock if not available
try:
    import gpiod  # pyright: ignore[reportMissingImports]
    from gpiod.line import Direction, Value, Bias  # pyright: ignore[reportMissingImports]
    HAS_GPIOD = True
except ImportError:
    HAS_GPIOD = False

    # Mock enums for testing without hardware
    class Direction:
        INPUT = "in"
        OUTPUT = "out"

    class Value:
        ACTIVE = 1
        INACTIVE = 0

    class Bias:
        PULL_UP = "pull_up"
        PULL_DOWN = "pull_down"
        DISABLED = "disable"

class HWGPIO:
    """
    Wrapper for a single GPIO line using gpiod.

    Provides read/write access with optional mock mode, state tracking,
    and callback listeners.

    Attributes:
        MOCK (bool): True if running without real gpiod hardware.
    """
    MOCK: bool = not HAS_GPIOD

    def __init__(
        self,
        gpio_offset: int,
        direction: Literal["in", "out"] = "in",
        bias: Optional[Literal["pull_up", "pull_down"]] = None,
        active_low: bool = False,
        chip_path: str = "/dev/gpiochip0"
    ):
        """
        Initialize a GPIO pin.

        Args:
            gpio_offset (int): GPIO line offset on the chip.
            direction (str): "in" or "out".
            bias (str | None): Optional pull-up/pull-down bias; None = disabled.
            active_low (bool): If True, logic is inverted.
            chip_path (str): Path to GPIO chip device.

        Notes:
            - In MOCK mode or on import failure, the pin operates in software-only mode.
            - Stores callbacks for state changes.
        """
        self.gpio_offset: int = gpio_offset
        self.gpio: int = gpio_offset
        self.direction: str = direction
        self._state: bool = False
        self.callbacks: List[Callable[['HWGPIO'], None]] = []
        self.request = None
        self.chip_path: str = chip_path

        # Convert bias string to gpiod enum
        if bias is None:
            bias = Bias.DISABLED
        elif bias == "pull_up":
            bias = Bias.PULL_UP
        elif bias == "pull_down":
            bias = Bias.PULL_DOWN

        # Attempt hardware line request if not in mock
        if not HWGPIO.MOCK:
            try:
                cfg = gpiod.LineSettings(
                    direction=Direction.OUTPUT if direction == "out" else Direction.INPUT,
                    output_value=Value.INACTIVE,
                    bias=bias,
                    active_low=active_low
                )
                self.request = gpiod.request_lines(
                    chip_path,
                    consumer="hwgpio",
                    config={gpio_offset: cfg}
                )
            except Exception:
                # Fallback to mock if initialization fails
                HWGPIO.MOCK = True
                self.request = None

    @property
    def state(self) -> bool:
        """
        Get the current GPIO state.

        Returns:
            bool: True if HIGH/active, False if LOW/inactive.

        Notes:
            - Returns internal _state in MOCK mode or if request failed.
        """
        if HWGPIO.MOCK or self.request is None:
            return self._state
        return bool(self.request.get_value(self.gpio_offset))

    @state.setter
    def state(self, val: bool) -> None:
        """
        Set the GPIO output state.

        Args:
            val (bool): True to set HIGH/active, False to set LOW/inactive.

        Notes:
            - Updates hardware only if direction is "out" and not in mock.
            - Triggers any registered callbacks after the state changes.
        """
        val = bool(val)
        if self._state == val:
            return

        if not HWGPIO.MOCK and self.request is not None and self.direction == "out":
            self.request.set_value(self.gpio_offset, Value.ACTIVE if val else Value.INACTIVE)

        self._state = val  # update internal state

        # Trigger callbacks
        for cb in self.callbacks:
            cb(self)

    def on(self) -> None:
        """Set GPIO HIGH/active."""
        self.state = True

    def off(self) -> None:
        """Set GPIO LOW/inactive."""
        self.state = False

    def add_listener(self, callback: Callable[['HWGPIO'], None]) -> None:
        """
        Add a callback listener for state changes.

        Args:
            callback (Callable): Function called with this HWGPIO instance on state change.
        """
        if callback not in self.callbacks:
            self.callbacks.append(callback)


class HWGPIO_MONITOR:
    """
    Global asynchronous monitor for HWGPIO pins.

    Periodically polls pins and calls registered callbacks on state change.

    Attributes:
        loop (asyncio.AbstractEventLoop): Event loop for polling.
        pins (List[HWGPIO]): Registered pins.
        running (bool): True if polling loop is active.
        poll_interval (float): Delay between polls in seconds.
    """
    loop = asyncio.new_event_loop()
    pins: List[HWGPIO] = []
    running: bool = False
    poll_interval: float = 0.01

    @classmethod
    def start(cls) -> None:
        """Start the monitor loop (non-blocking)."""
        if cls.running:
            return
        cls.running = True
        threading.Thread(target=cls.loop.run_forever, daemon=True).start()
        cls.loop.call_soon_threadsafe(cls.loop.create_task, cls._poll_loop())

    @classmethod
    def stop(cls) -> None:
        """Stop the monitor loop."""
        cls.running = False
        cls.loop.call_soon_threadsafe(cls.loop.stop)

    @classmethod
    def basic_callback(cls, p: HWGPIO) -> None:
        """Default callback: print pin state changes."""
        print(f"GPIO{p.gpio_offset} changed to {p.state}")

    @classmethod
    def add_listener(cls, pin: HWGPIO, callback: Optional[Callable[[HWGPIO], None]] = None) -> None:
        """
        Register a pin and callback for monitoring.

        Args:
            pin (HWGPIO): Pin instance to monitor.
            callback (Callable | None): Function called on state change. Defaults to basic_callback.
        """
        if callback is None:
            callback = cls.basic_callback
        pin.add_listener(callback)
        if pin not in cls.pins:
            cls.pins.append(pin)

    @classmethod
    async def _poll_loop(cls) -> None:
        """
        Asynchronous loop polling registered pins.

        Calls callbacks on state change.
        """
        last_states = {pin.gpio_offset: pin.state for pin in cls.pins}
        while cls.running:
            for pin in cls.pins:
                current = pin.state
                last = last_states.get(pin.gpio_offset)
                if last is None:
                    last_states[pin.gpio_offset] = current
                    continue
                if last != current:
                    last_states[pin.gpio_offset] = current
                    for cb in pin.callbacks:
                        cb(pin)
            await asyncio.sleep(cls.poll_interval)



if __name__ == "__main__":
    HWGPIO.MOCK = False
    HWGPIO_MONITOR.start()
    p = HWGPIO(21,"in", "pull_up")

    def callback(p:HWGPIO):
        print(f"gpio{p.gpio} changed to {p.state}")

    HWGPIO_MONITOR.add_listener(p, callback)
    input("enter to exit")

