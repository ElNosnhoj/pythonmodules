from setuptools import setup, find_packages

setup(
    name="pcf8574",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "i2c>=0.1.0",  # your i2c package
        "smbus2"
    ],
    description="PCF8574 I2C IO expander wrapper with optional mock support",
    author="nos",
    python_requires=">=3.7",
)
