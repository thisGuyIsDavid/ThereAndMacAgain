import serial

gps_serial_reader = serial.Serial(
			port='ttyUSB0',
			baudrate=9600,
			parity=serial.PARITY_NONE,
			stopbits=serial.STOPBITS_ONE,
			bytesize=serial.EIGHTBITS,
			timeout=1
		)

while True:
    try:

        gps_message = gps_serial_reader.readline()
        gps_message = gps_message.decode(('utf-8').strip())
        if gps_message == "":
            continue
        print(gps_message)

    except Exception as e:
        continue