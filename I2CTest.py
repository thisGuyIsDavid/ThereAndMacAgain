from app.displays import I2CDisplayDriver
from time import *

mylcd = I2CDisplayDriver.lcd()

mylcd.lcd_display_string("Hello World!", 1)