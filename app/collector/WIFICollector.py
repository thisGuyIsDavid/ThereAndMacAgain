# !/usr/bin/env python
from app.collector.SerialCollector import SerialCollector


class WIFICollector(SerialCollector):

    def process_line(self, line):
        wifi_array = line.strip().replace("\n", "").split('|')

        return {
            "mac_address": wifi_array[0],
            "name": wifi_array[1]
        }
