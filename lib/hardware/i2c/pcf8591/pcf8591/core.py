#===================================================================
# PCF8591
# desc: 4-channel ADC + 1-channel DAC combo over I2C
#===================================================================
from i2c import NosI2CDevice

class PCF8591(NosI2CDevice):
    """
    Driver for the PCF8591 4-ADC + 1-DAC I2C module.

    Attributes:
        DEF_ADDR (int): Default I2C address.
        vref (float): Reference voltage for ADC/DAC conversion.
    """
    DEF_ADDR: int = 0x48
    
    # Control bytes for input channels
    CTRL_AD_CH0 = 0b00000000
    CTRL_AD_CH1 = 0b00000001
    CTRL_AD_CH2 = 0b00000010
    CTRL_AD_CH3 = 0b00000011
    CTRL_INC_FLAG = 0b00000100

    CTRL_ANALOG_OUTPUT_ENABLE = 0b01000000
    
    def __init__(self, addr: int = None, vref: float = 5.0, **kwargs):
        """
        Initialize the PCF8591 device.

        Args:
            addr (int): I2C address. Defaults to DEF_ADDR.
            vref (float): Reference voltage (default 5V).
        """
        if addr is None:
            addr = self.DEF_ADDR
        self.vref: float = vref
        super().__init__(addr, **kwargs)

    def set_value(self, value: float | int) -> None:
        """
        Set DAC output value (0–255).

        Args:
            value (int | float): DAC value to set.
        """
        # Clamp to 0–255
        value = max(0, min(255, int(value)))
        self.i2c.write_byte_data(self.addr, 0x40, value)

    def read_analog(self, ch: int) -> int:
        """
        Read ADC value from a given channel.

        Args:
            ch (int): ADC channel (0–3).

        Returns:
            int: 8-bit ADC value (0–255).

        Notes:
            - The first read after switching channel returns previous value,
              so a dummy read is performed first.
        """
        assert 0 <= ch <= 3, "Channel must be 0–3"
        # Select ADC channel
        self.i2c.write_byte(self.addr, 0x40 + ch)
        # Dummy read
        self.i2c.read_byte(self.addr)
        # Actual ADC read
        return self.i2c.read_byte(self.addr)

    def get_voltage(self, ch: int, r: int = 3) -> float:
        """
        Convert ADC reading to voltage.

        Args:
            ch (int): ADC channel (0–3).
            r (int): Number of decimal places to round.

        Returns:
            float: Voltage corresponding to ADC value.
        """
        assert 0 <= ch <= 3, "Channel must be 0–3"
        adc_val = self.read_analog(ch)
        voltage = adc_val * self.vref / 255
        return round(voltage, r)

    def set_voltage(self, volt: float) -> None:
        """
        Set DAC output voltage.

        Args:
            volt (float): Voltage to output (0–vref).

        Notes:
            - Voltage is clamped to [0, vref] and converted to 8-bit DAC value.
        """
        # Clamp to vref
        volt = max(0.0, min(self.vref, volt))
        val = volt * 255 / self.vref
        self.set_value(val)

if __name__ == "__main__":
    pcf = PCF8591(vref=5.234)
    pcf.set_voltage(1.2)
    pcf.get_voltage(0)