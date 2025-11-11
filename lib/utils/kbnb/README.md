# lib/utils/kbnb

## Installation
via https
```
pip install git+https://github.com/ElNosnhoj/pythonmodules.git@main#subdirectory=lib/utils/kbnb
```

via ssh
```
pip install git+ssh://git@github.com:ElNosnhoj/pythonmodules.git@main#subdirectory=lib/utils/kbnb

```

via local
```
pip install <path>/pythonmodules/lib/utils/kbnb
```

to uninstall
```
pip uninstall kbnb
```


## Usage
```python
from kbnb import kb
while True:
    if kb.kbhit():
        c = kb.getch()
        if ord(c) == 27: # ESC
            break
        print(c)
            
kb.set_normal_term()
```



