# !/usr/bin/env python
from app.collector.SerialCollector import SerialCollector


class WIFICollector(SerialCollector):
    vendor_map = {}

    def process_line(self, line):
        wifi_array = line.strip().replace("\n", "").split('|')

        return {
            "mac_address": wifi_array[0],
            "name": wifi_array[1]
        }

    def setup(self):
        self.set_collector()
        with open('/home/pi/vendors.txt', encoding='utf-8') as vendor_list:
            for line in vendor_list:
                line = line.strip().split('\t')
                self.vendor_map[line[0]] = line[1]


