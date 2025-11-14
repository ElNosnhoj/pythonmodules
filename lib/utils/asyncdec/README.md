# lib/utils/asyncdec

## Installation
via https
```
pip install git+https://github.com/ElNosnhoj/pythonmodules.git@main#subdirectory=lib/utils/asyncdec
```

via ssh
```
pip install git+ssh://git@github.com:ElNosnhoj/pythonmodules.git@main#subdirectory=lib/utils/asyncdec

```

via local
```
pip install <path>/pythonmodules/lib/utils/asyncdec
```

to uninstall
```
pip uninstall asyncdec
```


## Usage
non blocking function
```python
from asyncdec import AsyncManager
import time
@async_fire_and_forget
def hello():
    for i in range(5):
        print("hello")
        time.sleep(1)
    print("goodbye")
hello()
input("...")
```
example async manager with emergency stop
```python
from asyncdec import AsyncManager
import time
ars = AsyncManager("ars")
on_start = lambda: print("start")
on_done = lambda: print("done")
on_exception = lambda: print("exception")

@ars.operation(timeout=20.0, on_start=on_start, on_done=on_done, on_exception=on_exception)
def some_operation():
    print("doing some operation")
    for i in range(20):
        time.sleep(1)

some_operation()
time.sleep(5)
ars.emergency_stop()
```



