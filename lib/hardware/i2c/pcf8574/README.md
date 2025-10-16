# lib/hardware/i2c/pcf8574

Interface PCF8574 I2C IO expander.

## Requirements
needs i2c library. look at 
```
https://github.com/ElNosnhoj/pythonmodules/tree/main/lib/hardware/i2c/i2c
```

## Installation
via https
```
pip install git+https://github.com/ElNosnhoj/pythonmodules.git@main#subdirectory=lib/hardware/i2c/pcf8574
```

via ssh
```
pip install git+ssh://git@github.com:ElNosnhoj/pythonmodules.git@main#subdirectory=lib/hardware/i2c/pcf8574
```

via local
```
pip install <path>/pythonmodules/lib/hardware/i2c/pcf8574
```

uninstall
```
pip uninstall pcf8574
```

## Usage
```python
from pcf8574 import PCF8574
from i2c import NosI2C
i2c = NosI2C()
bus = PCF8574(0x20,i2c=i2c)
state = bus.get_state()
print(state)
```


