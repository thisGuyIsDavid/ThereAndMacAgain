
from app.displays import I2CDisplayDriver


class Display:

    def __init__(self):
        try:
            self.display = I2CDisplayDriver.lcd()
        except Exception as e:
            #   in prototyping, the screen may not be attached. Live with it.
            self.display = None

    def set_message(self, line_1, line_2):
        if self.display is None:
            return
        self.display.lcd_clear()
        self.display.lcd_display_string(line_1, 1)
        self.display.lcd_display_string(line_2, 2)

    def clear(self):
        if self.display is None:
            self.display.lcd_clear()