#===================================================================
# PCA9685
# desc: 16 channel servo driver
#===================================================================
from i2c import NosI2CDevice, NosI2C
import time


class PCA9685(NosI2CDevice):
    """
    Driver for the PCA9685 16-channel 12-bit PWM controller over I2C.

    Provides PWM outputs with configurable frequency and duty cycle,
    with optional mock mode if no I2C hardware is present.

    Attributes:
        MOCK (bool): True if running without actual I2C hardware.
        REG_* (int): Register addresses for PWM channels and control.
    """

    MOCK: bool = not NosI2C.HAS_I2C

    # Base registers for PWM channels (channel 1)
    REG_PWM1_ON_L: int  = 0x06  # Low byte for ON count
    REG_PWM1_ON_H: int  = 0x07  # High byte for ON count
    REG_PWM1_OFF_L: int = 0x08  # Low byte for OFF count
    REG_PWM1_OFF_H: int = 0x09  # High byte for OFF count
    
    # Control registers
    REG_MODE1: int    = 0x00  # Mode register 1 (sleep, restart, etc.)
    REG_PRESCALE: int = 0xFE  # Prescale register for PWM frequency

    def __init__(self, addr: int = 0x40, **kwargs):
        """
        Initialize the PCA9685 device.

        Args:
            addr (int): I2C address of the device (default 0x40).
            **kwargs: Additional parameters for the base NosI2CDevice.

        Notes:
            - In MOCK mode, the device does not attempt I2C initialization.
            - Otherwise, calls the base NosI2CDevice constructor.
        """
        if PCA9685.MOCK:
            # Skip hardware initialization if running in mock mode
            return

        # Initialize the base I2C device with the given address
        super().__init__(addr, **kwargs)

        
    def reset(self):
        """
        Reset the PCA9685 device.

        This clears the MODE1 register and sets the chip to its default state.
        All PWM channels will be turned off, and the internal 12-bit counter
        will start from 0.

        Notes:
            - Typical use: called during initialization to ensure a known state.
            - Waits 200ms to allow the device to stabilize after reset.
        """
        # Write 0x00 to MODE1 register to reset the chip
        self.write_reg_byte(self.REG_MODE1, 0x00)
        
        # Delay to allow reset to take effect
        time.sleep(0.2)


    def restart(self):
        """
        Restart the PCA9685 device after sleep or configuration changes.

        This sets the RESTART bit in MODE1 register, which causes the internal
        counter to start from 0 and resumes PWM output.

        Notes:
            - Typically called after changing prescale (frequency) or exiting sleep.
            - Waits 200ms to allow the device to stabilize after restart.
        """
        # Write 0x80 to MODE1 register to set the RESTART bit
        self.write_reg_byte(self.REG_MODE1, 0x80)
        
        # Delay to allow restart to complete
        time.sleep(0.2)

    def set_freq(self, freq: float):
        """
        Set the PWM frequency for all channels.

        Parameters:
            freq (float): Desired frequency in Hz (24–1526 Hz)

        Notes:
            - The PCA9685 has a 25 MHz internal oscillator and 12-bit counter.
            - The prescale register is calculated as: prescale = round(25_000_000 / (4096 * freq) - 1)
            - The chip must be put to sleep to write the prescale, then restarted.
        """
        # Validate frequency range
        assert 24 <= freq <= 1526, f"Frequency {freq} Hz out of range (24–1526 Hz)"

        # Calculate prescale value from datasheet formula
        pre = int((25_000_000 / (4096 * freq)) - 1)

        if PCA9685.MOCK:
            self.__mock["freq"] = freq
            return

        # Enter sleep mode to allow prescale update
        self.write_reg_byte(self.REG_MODE1, 0x10)
        # Write prescale value
        self.write_reg_byte(self.REG_PRESCALE, pre)
        # Restart the device
        self.restart()

    def set_pwm(self,ch:int,on:int,off:int):
        """
        Set the ON and OFF counts for a specific PCA9685 channel.

        Each channel has a 12-bit counter (0–4095) that repeats continuously.
        The output goes HIGH when counter == ON and LOW when counter == OFF.

        Parameters:
            ch (int): Channel number (0–15)
            on (int): Counter value to start the pulse (0–4095)
            off (int): Counter value to end the pulse (0–4095)

        Notes:
            - Wraparound is handled by the hardware if off < on.
            - For 100% duty cycle, use on=0, off=4095 or set FULL_ON bit.
            - For 0% duty cycle, use on=0, off=0 or set FULL_OFF bit.
        """
        # Validate inputs
        assert 0 <= ch < 16, "Channel must be 0–15"
        assert 0 <= on <= 0x0FFF, "on should be 0–4095"
        assert 0 <= off <= 0x0FFF, "off should be 0–4095"

        # Calculate base register for this channel
        reg = self.REG_PWM1_ON_L + ch * 4

        # Write the 12-bit ON count to two registers (low + high byte)
        self.write_reg_byte(reg + 0, on & 0xFF)
        self.write_reg_byte(reg + 1, on >> 8)

        # Write the 12-bit OFF count to two registers (low + high byte)
        self.write_reg_byte(reg + 2, off & 0xFF)
        self.write_reg_byte(reg + 3, off >> 8)
        

    def set_duty_cycle(self, ch: int, duty: float, shift: float = 0):
        """
        Set PWM duty cycle (0–100%) for a channel with optional phase shift.

        Parameters:
            ch (int): Channel number (0–15)
            duty (float): Duty cycle percentage (0–100)
            shift (float): Phase shift percentage (0–100), optional. 
                        0 = pulse starts at beginning of PWM cycle.

        Notes:
            - The ON/OFF counts are calculated relative to the internal 12-bit counter (0–4095).
            - Wraparound is automatically handled if shift + duty exceeds 4095.
            - For 100% duty cycle, duty=100 will generate a full ON pulse.
            - For 0% duty cycle, duty=0 will generate a full OFF pulse.
        """
        # Validate inputs
        assert 0 <= ch < 16, "Channel must be 0–15"
        assert 0 <= duty <= 100, "Duty should be 0–100"
        assert 0 <= shift <= 100, "Shift should be 0–100"
        assert duty + shift <= 100, "Duty + shift must be <= 100%"

        # Convert percentage to 12-bit counts
        duty_count = int((duty / 100.0) * 4095)
        shift_count = int((shift / 100.0) * 4095)

        # Compute ON/OFF counts (wraparound automatically handled)
        on = shift_count & 0x0FFF
        off = (on + duty_count) & 0x0FFF

        # Apply the PWM settings
        self.set_pwm(ch, on, off)

    def get_pwm(self, ch: int)->tuple[int,int]:
        """
        Read the current ON and OFF counts for a specific PCA9685 channel.

        Parameters:
            ch (int): Channel number (0–15)

        Returns:
            tuple: (on, off) — 12-bit counter values indicating when the output
                goes HIGH (on) and LOW (off) during the PWM cycle.

        Notes:
            - Each channel has a 12-bit counter (0–4095) that repeats continuously.
            - The ON/OFF counts determine the PWM pulse: 
                output HIGH when counter == ON, 
                output LOW when counter == OFF.
            - Values are read from the following registers:
                ON_L, ON_H, OFF_L, OFF_H
            - Wraparound is handled automatically by the PCA9685.
            - For 100% duty cycle, the FULL_ON bit may be set, but this method
            will return the raw register values (you may need separate logic to interpret FULL_ON / FULL_OFF flags).
            - This method can also be used in MOCK mode to inspect simulated PWM values.
        """
        # Validate channel
        assert 0 <= ch < 16, "Channel must be 0–15"

        # Base register for this channel
        base = self.REG_PWM1_ON_L + ch * 4

        # Read 12-bit ON count
        on_l  = self.read_reg_byte(base + 0)
        on_h  = self.read_reg_byte(base + 1)

        # Read 12-bit OFF count
        off_l = self.read_reg_byte(base + 2)
        off_h = self.read_reg_byte(base + 3)

        # Combine low/high bytes into 12-bit counts
        on  = (on_h << 8) | on_l
        off = (off_h << 8) | off_l

        return (on, off)

    def get_duty_cycle(self, ch: int)->tuple[float,float]:
        """
        Get the current PWM duty cycle and phase shift for a channel.

        Parameters:
            ch (int): Channel number (0–15)

        Returns:
            tuple: (duty, shift) in percent
                - duty: percentage of the PWM cycle the output is HIGH (0–100%)
                - shift: phase shift as percentage of the PWM cycle (0–100%)

        Notes:
            - This uses the raw ON/OFF counts from the PCA9685 registers.
            - Wraparound is handled automatically.
            - For FULL_ON or FULL_OFF bits, this will return approximate values 
            based on the register counts. For exact detection, additional checks
            for FULL_ON/FULL_OFF would be needed.
        """
        # Validate channel
        assert 0 <= ch < 16, "Channel must be 0–15"

        # Read raw ON/OFF 12-bit counts
        on, off = self.get_pwm(ch)

        # Compute duty count, handling wraparound
        # If off < on, pulse wraps past 4095, so we use modulo 4096
        duty_count = (off - on) & 0x0FFF

        # Convert to percentage of the full 12-bit cycle
        duty = duty_count / 4095 * 100

        # Compute phase shift as percentage of the full cycle
        shift = on / 4095 * 100

        return duty, shift


if __name__ == "__main__":
    pca = PCA9685(0x41)
    pca.set_freq(500)
    pca.set_duty_cycle(0,50,10)
    print(pca.get_pwm(0))
