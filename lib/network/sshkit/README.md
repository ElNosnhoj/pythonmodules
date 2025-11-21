# lib/network/sshkit
ssh client. just wraps paramiko.

## Installation
via https
```
pip install git+https://github.com/ElNosnhoj/pythonmodules.git@main#subdirectory=lib/network/sshkit
```

via ssh
```
pip install git+ssh://git@github.com:ElNosnhoj/pythonmodules.git@main#subdirectory=lib/network/sshkit
```

via local
```
pip install <path>/pythonmodules/lib/network/sshkit
```

uninstall
```
pip uninstall sshkit
```

## usage
```python
import sshkit
client = sshkit.Client("192.168.1.10", user="user", pswd="pswd")
code, out, err = client.exec_parse("echo hello")
if code == 0: print(out)
```

