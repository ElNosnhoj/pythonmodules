# lib/network/ip_scanner

scan ips

## Installation
via https
```
pip install git+https://github.com/ElNosnhoj/pythonmodules.git@main#subdirectory=lib/network/ip_scanner
```

via ssh
```
pip install git+ssh://git@github.com:ElNosnhoj/pythonmodules.git@main#subdirectory=lib/network/ip_scanner
```

via local
```
pip install <path>/pythonmodules/lib/network/ip_scanner
```

uninstall
```
pip uninstall ip_scanner
```

## usage
```python
import ip_scanner
ips = ip_scanner.get_ips(base="192.168.1.", start=2, end=254)
```

