# hardware/pigpiod

Control Raspberry Pi GPIO using gpiod with optional mock support for testing.

## Installation
via ssh
```
pip install "git+ssh://git@github.com/ElNosnhoj/pythonmodules.git@main#egg=pigpiod&subdirectory=lib/hardware/pigpiod"
```

via https
```
pip install "git+https://github.com/ElNosnhoj/pythonmodules.git@main#egg=pigpiod&subdirectory=lib/hardware/pigpiod"
```

via local clone
```
pip install "<path_to_repo>/pythonmodules/lib/hardware/pigpiod"
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
pin5.state=1
input("")
pin5.state=0
```

monitor
```python
from pigpiod import HWGPIO, HWGPIO_MONITOR
HWGPIO_MONITOR.start()

pin5 = HWGPIO(5, "out")
pin14 = HWGPIO(14,"in")

def sensor_cb(p:HWGPIO): 
    pin5.state=p.state
def hello(p:HWGPIO):
    print("hello")

HWGPIO_MONITOR.add_listener(pin14, sensor_cb)

input("Press Enter to turn on...")
pin5.state=1
input("Press Enter to turn off...")
pin5.state=0
```