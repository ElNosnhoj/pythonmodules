# hardware/i2c/pcf8574

## Requirements
needs i2c library. look at 
```
https://github.com/ElNosnhoj/pythonmodules/tree/main/lib/hardware/i2c/i2c
```

## Installation
via ssh
```
pip install "git+ssh://git@github.com/ElNosnhoj/pythonmodules.git@main#egg=i2c&subdirectory=lib/hardware/i2c/pcf8574"
```

via https
```
pip install "git+https://github.com/ElNosnhoj/pythonmodules.git@main#egg=i2c&subdirectory=lib/hardware/i2c/pcf8574"
```

via local clone
```
pip install "<path_to_repo>/pythonmodules/lib/hardware/i2c/pcf8574"
```

uninstall
```
pip uninstall pcf8574
```

## Usage
```python
from pcf8574 import PCF8574
from i2c import NosI2C()
i2c = NosI2C()
bus = PCF8574(0x20,i2c=i2c)
state = bus.get_state()
print(state)
```


