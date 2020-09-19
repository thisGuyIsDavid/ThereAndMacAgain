# !/usr/bin/env python
import serial


class SerialCollector:

    def __init__(self, serial_port):
        self.serial_port = serial_port
        self.serial_reader = None
        self.is_reading = False

    def set_collector(self):
        if self.serial_port is None:
            return

        self.serial_reader = serial.Serial(
            port=self.serial_port,
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

    def get_line(self):
        raw_line = self.serial_reader.readline()
        raw_line = raw_line.decode('utf-8').strip()
        if raw_line == "":
            return
        return self.process_line(raw_line)

    def process_line(self, line):
        pass


