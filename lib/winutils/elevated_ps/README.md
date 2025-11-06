# lib/winutils/elevated_ps

## Installation
via https
```
pip install git+https://github.com/ElNosnhoj/pythonmodules.git@main#subdirectory=lib/winutils/elevated_ps
```

via ssh
```
pip install git+ssh://git@github.com:ElNosnhoj/pythonmodules.git@main#subdirectory=lib/winutils/elevated_ps

```

via local
```
pip install <path>/pythonmodules/lib/winutils/elevated_ps
```

to uninstall
```
pip uninstall elevated_ps
```


## Usage
```python
import elevated_ps
cmd = f"""echo 'This is run from elevated ps1'"""
out, err = elevated_ps.run(cmd)
print(out)
```



