# lib/hardware/i2c/pca9685

Interface PCF8574 I2C IO expander.

## Requirements
needs i2c library. look at 
```
https://github.com/ElNosnhoj/pythonmodules/tree/main/lib/hardware/i2c/i2c
```

## Installation
via https
```
pip install git+https://github.com/ElNosnhoj/pythonmodules.git@main#subdirectory=lib/hardware/i2c/pca9685
```

via ssh
```
pip install git+ssh://git@github.com:ElNosnhoj/pythonmodules.git@main#subdirectory=lib/hardware/i2c/pca9685
```

via local
```
pip install <path>/pythonmodules/lib/hardware/i2c/pca9685
```

uninstall
```
pip uninstall pca9685
```

## Usage
```python
from pca9685 import PCA9685
pca = PCA9685(0x41)
pca.set_freq(500)
pca.set_duty_cycle(0,50,10)
print(pca.get_pwm(0))
```


