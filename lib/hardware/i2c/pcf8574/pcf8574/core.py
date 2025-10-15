#===================================================================
# PCF8574
# desc: I2C io expansion has interrupt pin but not handled yet
#===================================================================
from typing import Union
from i2c import NosI2CDevice, NosI2C

# byte |= 1 << p      # high
# byte &= ~(1 << p)   # low
# byte ^= 1 << p      # toggle

# mock detector
try:
    from smbus2 import SMBus
    import os
    _HAS_I2C = os.path.exists("/dev/i2c-1")
except ImportError:
    print("!![PCF8574] smbus2 not installed. FORCING MOCK")
    _HAS_I2C = False

if not _HAS_I2C:
    print("!![PCF8574] System has no i2c-1 support. FORCING MOCK")


class PCF8574(NosI2CDevice):
    MOCK = not _HAS_I2C
    __max_p = 7
    def __init__(self, addr=0x20, **kwargs):
        self.__mock = 0xff
        if PCF8574.MOCK: return
        super().__init__(addr, **kwargs)

    def read_byte(self):
        return self.__mock if PCF8574.MOCK else super().read_byte()
    def write_byte(self, value:int):
        if PCF8574.MOCK: self.__mock = value & 0xff
        else: super().write_byte(value)

    def get_state(self, p:Union[int,None]=None):
        assert p is None or p in range(8)
        b = self.read_byte()
        return [(b >> i) & 1 == 1 for i in range(8)] if p==None else bool(b&1<<p)

    def set_state(self, p:int, value:Union[int,bool]):
        assert p in range(8)
        byte = self.read_byte()

        if isinstance(value,int):
            value = value & 0xff
            if value==byte: return
            self.write_byte(value)
        elif isinstance(value,bool):
            if bool(byte&1<<p) == value: return
            if value: byte |= 1 << p
            else: byte &= ~(1 << p) 
            self.write_byte(byte)

if __name__ == "__main__":
    PCF8574.MOCK=True
    i2c = NosI2C()
    bus = PCF8574(0x20,i2c=i2c)
    state = bus.get_state()
    print(state)