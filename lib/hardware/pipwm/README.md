# lib/hardware/pipwm

Control Raspberry Pi hardware PWM via sysfs.

## Prerequisite
copy under [all] of /boot/firmware/config.txt and reboot
for ch to gpio 0:12,1:13 
```
dtoverlay=pwm-2chan,pin=12,func=4,pin2=13,func2=4
```
for ch to gpio 2:18, 3:19
```
dtoverlay=pwm-2chan,pin=18,func=4,pin2=19,func2=4
```
or simply 
```
dtoverlay=pwm-2chan
```

## Installation
via https
```
pip install git+https://github.com/ElNosnhoj/pythonmodules.git@main#subdirectory=lib/hardware/pipwm
```

via ssh
```
pip install git+ssh://git@github.com:ElNosnhoj/pythonmodules.git@main#subdirectory=lib/hardware/pipwm
```

via local
```
pip install <path>/pythonmodules/lib/hardware/pipwm
```

uninstall
```
pip uninstall pipwm
```

## usage
```python
from pipwm import HWPWM
pwm = HWPWM(0)
pwm.start(25000, 50)
```

