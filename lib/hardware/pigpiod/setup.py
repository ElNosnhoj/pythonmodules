from setuptools import setup, find_packages

setup(
    name="pigpiod",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "gpiod; sys_platform=='linux'",
        "asyncio",
    ],
    python_requires=">=3.8",
    description="Raspberry Pi GPIO utilities with mock support",
    author="nos",
)
