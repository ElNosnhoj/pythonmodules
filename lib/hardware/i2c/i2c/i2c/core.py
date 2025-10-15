#===================================================================
# file: i2c.py
# desc: interfacing i2c. 
# dev : nos
# os :  
#   * linux
# todo :
#   * windows
#===================================================================
from typing import List, Union
import smbus2

class NosI2C(smbus2.SMBus):
    class NO_ADDR_PROVIDED(Exception):pass

    @classmethod
    def discover(cls,bus=1):
        """ just loop reads bus. blocking """
        import time
        i2c = NosI2C(bus)
        _addresses = i2c.scan()
        print("scanned addresses: %s" % ([hex(i) for i in _addresses]))
        while True:
            addresses = i2c.scan()
            if addresses == _addresses: continue
            _addresses = addresses
            print("scanned addresses: %s" % ([hex(i) for i in _addresses]))
            time.sleep(1)


    def __init__(self,bus=1):
        """ NosI2C """
        super().__init__(bus)
    
    def scan(self):
        """ scan for devices on bus """
        res = []
        for a in range(0x7f):
            try:
                self.read_byte(a)
                res.append(a)
            except OSError:
                pass
        return res
    
    # def writeto(self,addr,data):
    #     """ write straight to address. no register. """
    #     m = smbus2.i2c_msg.write(addr,data)
    #     self.i2c_rdwr(m)

    # def readfrom(self,addr,nbytes=1):
    #     """ read straight from address. no register. """
    #     m=smbus2.i2c_msg.read(addr,nbytes)
    #     self.i2c_rdwr(m)
    #     return list(m)
    
class NosI2CDevice:
    DEF_ADDR = None
    class NO_ADDR_PROVIDED(Exception):pass
    def __init__(self,addr=None,**kwargs):
        if addr==None and self.DEF_ADDR==None: raise NosI2CDevice.NO_ADDR_PROVIDED
        self.addr=self.DEF_ADDR
        if addr: self.addr=addr
        
        i2c=kwargs.pop("i2c",None)
        if i2c: 
            self.i2c=i2c       
        else:
            self.i2c = NosI2C()
        self.init(kwargs=kwargs)
    
    def init(self, **kwargs):
        return
    
    def read_byte(self) -> int:
        """ read one byte directly. no register pointer """
        return self.i2c.read_byte(self.addr)
    
    def read_reg_byte(self, reg:int, amnt=1)->int:
        """ read byte(s) from given register """
        if amnt==1:
            return self.i2c.read_byte_data(self.addr, reg)
        else:
            return self.i2c.read_i2c_block_data(self.addr,reg,amnt)
    def read_reg_word(self, reg:int)->int:
        """ read one word from given register. ie 2 bytes"""
        return self.i2c.read_word_data(self.addr,reg)

    def write_byte(self, value:int):
        """ write byte directly. no register pointer """
        self.i2c.write_byte(self.addr, value & 0xff)
    def write_reg_byte(self, reg:int, value: Union[int, List[int]]):
        """ write byte(s) to given register """
        if isinstance(value,int):
            self.i2c.write_byte_data(self.addr,reg,value&0xff)
        elif isinstance(value,list):
            self.i2c.write_i2c_block_data(self.addr,reg,[v&0xff for v in value])
    def write_reg_word(self,reg:int, value:int):
        """ write one word to given register """
        self.i2c.write_word_data(self, reg, value&0xffff)
    

if __name__ == "__main__":
    NosI2C.discover()
    

    