# lib/hardware/i2c/i2c

## Installation
via https
```
pip install git+https://github.com/ElNosnhoj/pythonmodules.git@main#subdirectory=lib/hardware/i2c/i2c
```

via ssh
```
pip install git+ssh://git@github.com:ElNosnhoj/pythonmodules.git@main#subdirectory=lib/hardware/i2c/i2c

```

via local
```
pip install <path>/pythonmodules/lib/hardware/i2c/i2c
```


to uninstall
```
pip uninstall i2c
```

## Usage
```python
from i2c import NosI2C, NosI2CDevice
# create an I2C bus instance (defaults to /dev/i2c-1)
bus = NosI2C()

# scan for connected devices
addresses = bus.scan()
print("Found devices:", addresses)

# create a device instance for address 0x20
device = NosI2CDevice(addr=0x20, i2c=bus)

# read and write a single byte
byte = device.read_byte()
device.write_byte(0xFF)

# read and write registers
reg_val = device.read_reg_byte(0x01)
device.write_reg_byte(0x01, 0xAA)
```


