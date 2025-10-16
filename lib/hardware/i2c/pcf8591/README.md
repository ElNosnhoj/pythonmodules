# lib/hardware/i2c/pcf8591

PCF8591 4-channel ADC + 1-channel DAC I2C module wrapper with optional mock support

## Requirements
needs i2c library. look at 
```
https://github.com/ElNosnhoj/pythonmodules/tree/main/lib/hardware/i2c/i2c
```

## Installation
via https
```
pip install git+https://github.com/ElNosnhoj/pythonmodules.git@main#subdirectory=lib/hardware/i2c/pcf8591
```

via ssh
```
pip install git+ssh://git@github.com:ElNosnhoj/pythonmodules.git@main#subdirectory=lib/hardware/i2c/pcf8591
```

via local
```
pip install <path>/pythonmodules/lib/hardware/i2c/pcf8591
```

uninstall
```
pip uninstall pcf8591
```

## Usage
setting out voltage
```python
from pcf8591 import PCF8591
pcf = PCF8591(vref=5.234)
pcf.set_voltage(1.2)
```

reading analog voltage
```python
from pcf8591 import PCF8591
pcf = PCF8591(vref=5.234)
v0 = pcf.get_voltage(0)
```


