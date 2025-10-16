# lib/hardware/pigpiod

Control Raspberry Pi GPIO using gpiod with optional mock support for testing.

## Installation
via https
```
pip install git+https://github.com/ElNosnhoj/pythonmodules.git@main#subdirectory=lib/hardware/pigpiod
```

via ssh
```
pip install git+ssh://git@github.com:ElNosnhoj/pythonmodules.git@main#subdirectory=lib/hardware/pigpiod
```

via local
```
pip install <path>/pythonmodules/lib/hardware/pigpiod
```

uninstall
```
pip uninstall pigpiod
```

## usage
enable mock
```python
from pigpiod import HWGPIO
HWGPIO.MOCK=True
```


basic
```python
from pigpiod import HWGPIO
pin5 = HWGPIO(5, "out")
input("Press Enter to turn on...")
pin5.state=1
input("Press Enter to turn off...")
pin5.state=0
```

monitor
```python
from pigpiod import HWGPIO, HWGPIO_MONITOR
HWGPIO_MONITOR.start()
p = HWGPIO(21,"in", "pull_up")

def callback(p:HWGPIO):
    print(f"gpio{p.gpio} changed to {p.state}")

HWGPIO_MONITOR.add_listener(p, callback)
input("enter to exit")
```