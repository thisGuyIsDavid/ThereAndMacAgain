# !/usr/bin/env python
from app.collector.SerialCollector import SerialCollector


class WIFICollector(SerialCollector):
    vendor_map = {}

    def process_line(self, line):
        wifi_array = line.strip().replace("\n", "").split('|')
        mac_address = str(wifi_array[0])
        mac_address_key = mac_address[:6].replace(':', '').upper()



        return {
            "mac_address":mac_address,
            "name": wifi_array[1],
            "key":mac_address_key
        }

    def setup(self):
        self.set_collector()
        with open('/home/pi/vendors.txt', encoding='utf-8') as vendor_list:
            for line in vendor_list:
                line = line.strip().split('\t')
                self.vendor_map[line[0]] = line[1]


