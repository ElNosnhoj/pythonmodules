#===================================================================
# pigpiod
# desc: control rpi5 gpio with mock for use with testing
#       uses gpiod and not sysfs
#===================================================================
import asyncio
import threading

# Try importing real gpiod; fallback to mock if not available
try:
    import gpiod # pyright: ignore[reportMissingImports]
    from gpiod.line import Direction, Value, Bias # pyright: ignore[reportMissingImports]
    HAS_GPIOD = True
except ImportError:
    HAS_GPIOD = False
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
    MOCK = not HAS_GPIOD

    def __init__(self, gpio_offset:int, direction="in", bias=Bias.DISABLED, chip_path="/dev/gpiochip0"):
        self.gpio_offset = gpio_offset
        self.gpio = gpio_offset
        self.direction = direction
        self._state = False
        self.callbacks = []
        self.request = None
        self.chip_path = chip_path

        if not HWGPIO.MOCK:
            try:
                cfg = gpiod.LineSettings(
                    direction=Direction.OUTPUT if direction=="out" else Direction.INPUT,
                    output_value=Value.INACTIVE,
                    bias=bias
                )
                self.request = gpiod.request_lines(
                    chip_path,
                    consumer="hwgpio",
                    config={gpio_offset: cfg}
                )
            except Exception:
                HWGPIO.MOCK = True
                self.request = None

    @property
    def state(self):
        if HWGPIO.MOCK or self.request is None:
            return self._state
        return bool(self.request.get_value(self.gpio_offset))

    @state.setter
    def state(self, val):
        val = bool(val)
        if self._state == val:
            return

        if not HWGPIO.MOCK and self.request is not None and self.direction == "out":
            self.request.set_value(self.gpio_offset, Value.ACTIVE if val else Value.INACTIVE)

        self._state = val  # update after successful write

        for cb in self.callbacks:
            cb(self)

    def on(self): self.state = True
    def off(self): self.state = False

    def add_listener(self, callback):
        if callback not in self.callbacks:
            self.callbacks.append(callback)

class HWGPIO_MONITOR:
    loop = asyncio.new_event_loop()
    pins = []
    running = False
    poll_interval = 0.01

    @classmethod
    def start(cls):
        if cls.running:
            return
        cls.running = True
        threading.Thread(target=cls.loop.run_forever, daemon=True).start()
        cls.loop.call_soon_threadsafe(cls.loop.create_task, cls._poll_loop())

    @classmethod
    def stop(cls):
        cls.running = False
        cls.loop.call_soon_threadsafe(cls.loop.stop)

    @classmethod
    def basic_callback(cls,p:HWGPIO):
        print(f"GPIO{p.gpio_offset} changed to {p.state}")

    @classmethod
    def add_listener(cls, pin:HWGPIO, callback=None):
        if callback is None: callback = cls.basic_callback
        pin.add_listener(callback)
        if pin not in cls.pins:
            cls.pins.append(pin)

    @classmethod
    async def _poll_loop(cls):
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

    pin5 = HWGPIO(5, "out")
    pin14 = HWGPIO(14,"in")

    def sensor_cb(p:HWGPIO): 
        pin5.state=p.state
    def hello(p:HWGPIO):
        print("hello")

    HWGPIO_MONITOR.add_listener(pin14, sensor_cb)
    # HWGPIO_MONITOR.add_listener(pin5, hello)

    input("Press Enter to turn on...")
    pin5.state=1
    input("Press Enter to turn off...")
    pin5.state=0
