#===================================================================
# PCF8574
# desc: I2C io expansion has interrupt pin but not handled yet
#===================================================================
from typing import Union, List
from i2c import NosI2CDevice, NosI2C

# byte |= 1 << p      # high
# byte &= ~(1 << p)   # low
# byte ^= 1 << p      # toggle

class PCF8574(NosI2CDevice):
    """
    Driver for the PCF8574 I2C I/O expander.

    Provides 8 GPIO pins over I2C with optional inversion and mock support.
    
    Attributes:
        MOCK (bool): True if running without actual I2C hardware.
    """

    MOCK = not NosI2C.HAS_I2C

    def __init__(self, addr: int = 0x20, invert: bool = False, **kwargs):
        """
        Initialize the PCF8574 device.

        Args:
            addr (int): I2C address of the device (default 0x20).
            invert (bool): Invert logic levels if True (default False).
            **kwargs: Additional parameters for the base NosI2CDevice.
        """
        self.__mock: int = 0xFF  # Mock state (all pins HIGH by default)
        self.__invert: bool = invert

        if PCF8574.MOCK:
            # Skip hardware initialization in mock mode
            return

        # Initialize the base I2C device
        super().__init__(addr, **kwargs)

    def read_byte(self) -> int:
        """
        Read a byte representing the state of all 8 pins.

        Returns:
            int: 8-bit value, each bit representing a pin state (1=HIGH, 0=LOW).

        Notes:
            - Applies inversion if self.__invert is True.
            - Returns self.__mock in MOCK mode.
        """
        res: int = self.__mock if PCF8574.MOCK else super().read_byte()
        if self.__invert:
            res ^= 0xFF  # Invert all bits
        return res

    def write_byte(self, value: int) -> None:
        """
        Write a byte to set all 8 pins at once.

        Args:
            value (int): 8-bit value to write to the expander.

        Notes:
            - Applies inversion if self.__invert is True.
            - Updates self.__mock in MOCK mode.
        """
        if self.__invert:
            value ^= 0xFF

        if PCF8574.MOCK:
            self.__mock = value & 0xFF
        else:
            super().write_byte(value)
    byte = property(read_byte, write_byte)

    def get_state(self, p: Union[int, None] = None) -> Union[List[bool], bool]:
        """
        Get the state of one or all pins.

        Args:
            p (int | None): Pin number (0–7) to read, or None for all pins.

        Returns:
            bool | List[bool]: 
                - If p is specified: True if the pin is HIGH, False if LOW.
                - If p is None: List of 8 booleans for all pins [P0..P7].

        Notes:
            - Uses read_byte() internally, respecting inversion.
        """
        assert p is None or 0 <= p <= 7, "Pin number must be 0–7 or None"
        b: int = self.read_byte()

        if p is None:
            # Return all 8 pins as booleans
            return [(b >> i) & 1 == 1 for i in range(8)]
        else:
            # Return single pin as boolean
            return bool(b & (1 << p))

    def set_state(self, p: int, value: bool) -> None:
        """
        Set the state of a single pin.

        Args:
            p (int): Pin number (0–7) to modify.
            value (bool): True for HIGH, False for LOW.

        Notes:
            - Reads the current byte, modifies only the specified pin,
              and writes the updated byte back.
            - No action is taken if the pin is already at the requested state.
        """
        assert 0 <= p <= 7, "Pin number must be 0–7"

        value_bool: bool = bool(value)
        byte: int = self.read_byte()

        # Set or clear the bit corresponding to pin p
        if value_bool:
            byte |= (1 << p)
        else:
            byte &= ~(1 << p)

        # Only write if the value actually changed
        if byte != self.read_byte():
            self.write_byte(byte)

    state = property(get_state, set_state)


if __name__ == "__main__":
    PCF8574.MOCK=False
    i2c = NosI2C()
    bus = PCF8574(0x20,i2c=i2c)
    state = bus.get_state()
    print(state)