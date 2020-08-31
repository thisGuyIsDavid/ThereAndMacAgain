from app.WiFiDeviceReader import WiFiDeviceReader

if __name__ == '__main__':
    WiFiDeviceReader(
        wifi_serial_port='/dev/ttyUSB0',
        gps_serial_port='/dev/ttyUSB1',
        database_location='data.db'

    ).run()