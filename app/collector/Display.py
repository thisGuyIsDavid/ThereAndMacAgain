
from app.displays import I2CDisplayDriver


class Display:

    def __init__(self):
        self.display = I2CDisplayDriver.lcd()

    def set_message(self, line_1, line_2):
        self.display.lcd_clear()
        self.display.lcd_display_string(line_1, 1)
        self.display.lcd_display_string(line_2, 2)

    def clear(self):
        self.display.lcd_clear()