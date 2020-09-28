import time
import digitalio
import board
import adafruit_matrixkeypad


class Keypad:
    cols = [digitalio.DigitalInOut(x) for x in (board.D4, board.D17, board.D27)]
    rows = [digitalio.DigitalInOut(x) for x in (board.D22, board.D23, board.D25, board.D5)]
    keys = ((1, 2, 3), (4, 5, 6), (7, 8, 9), ("*", 0, "#"))

    def __init__(self):
        self.keypad = adafruit_matrixkeypad.Matrix_Keypad(self.rows, self.cols, self.keys)

    def get_key_value(self):
        keys = self.keypad.pressed_keys
        if keys:
            return keys
