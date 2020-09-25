from app.collector.MainCollector import MainCollector
from app.displays import I2CDisplayDriver

from time import *

mylcd = I2CDisplayDriver.lcd()

mylcd.lcd_display_string("Hello World!", 1)

if __name__ == '__main__':
    MainCollector(
        wifi_port='/dev/ttyUSB1',
        gps_port='/dev/ttyUSB0',
        database_location='/home/pi/tama.db'
    ).run()