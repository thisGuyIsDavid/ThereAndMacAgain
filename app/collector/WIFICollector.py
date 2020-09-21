# !/usr/bin/env python
from app.collector.SerialCollector import SerialCollector
import os

class WIFICollector(SerialCollector):
    vendor_map = {}

    def process_line(self, line):
        wifi_array = line.strip().replace("\n", "").split('|')
        mac_address = str(wifi_array[0])

        mac_address_key = mac_address.replace(':', '').upper()[:6]
        vendor = self.vendor_map.get(mac_address_key, None)

        return {
            "mac_address":mac_address,
            "name": wifi_array[1],
            "vendor": vendor
        }

    def setup(self):
        self.set_collector()
        if os.path.exists('/home/pi/vendors.txt'):
            with open('/home/pi/vendors.txt', encoding='utf-8') as vendor_list:
                for line in vendor_list:
                    line = line.strip().split('\t')
                    self.vendor_map[line[0]] = line[1]


