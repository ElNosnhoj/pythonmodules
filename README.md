# pythonmodules
```
my-multi-lib-repo/
├─ package_a/
│   ├─ setup.py
│   ├─ pyproject.toml  # optional
│   └─ package_a/
│       └─ __init__.py
├─ package_b/
│   ├─ setup.py
│   ├─ pyproject.toml
│   └─ package_b/
│       └─ __init__.py
├─ package_c/
│   ├─ setup.py
│   ├─ pyproject.toml
│   └─ package_c/
│       └─ __init__.py
└─ README.md
```
via https
```
pip install git+https://github.com/username/my-multi-lib-repo.git@main#egg=package_a&subdirectory=package_a
```

via https with token
pip install git+https://<token>@github.com/username/my-multi-lib-repo.git@main#egg=package_a&subdirectory=package_a

via ssh
pip install git+ssh://git@github.com/username/my-multi-lib-repo.git@main#egg=package_a&subdirectory=package_a

via local clone
git clone git@github.com:username/my-multi-lib-repo.git
pip install ./my-multi-lib-repo/package_a

ie setup.py
# package_b/setup.py
from setuptools import setup, find_packages

setup(
    name="package_b",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "package_a>=0.1.0",
        "numpy"
    ],
)

