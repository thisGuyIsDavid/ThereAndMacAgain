from rpi_ws281x import PixelStrip, Color


class StatusLights:
    PROGRAM_LIGHT = 0
    GPS_LIGHT = 1
    WIFI_LIGHT = 2
    MISC_LIGHT = 3
    PROCESS_LIGHT = 4

    def __init__(self):
        # set status lights
        self.status_light = PixelStrip(8, 18, 800000, 10, False, 100, 0)
        self.status_light.begin()

        for pin in [self.PROGRAM_LIGHT, self.GPS_LIGHT, self.WIFI_LIGHT, self.PROCESS_LIGHT, self.MISC_LIGHT]:
            self.set_light_status(pin, 0)

    def set_light(self, pin, color):
        self.status_light.setPixelColor(pin, color)
        self.status_light.show()

    def set_light_status(self, pin, status):
        if status == -1:
            self.set_light(pin, Color(255, 0, 0))

        if status == 0:
            self.set_light(pin, Color(0, 0, 0))

        if status == 1:
            self.set_light(pin, Color(0, 255, 0))

    def set_program_status(self, status):
        self.set_light_status(self.PROGRAM_LIGHT, status)

    def set_gps_status(self, status):
        self.set_light_status(self.GPS_LIGHT, status)

    def set_wifi_status(self, status):
        self.set_light_status(self.WIFI_LIGHT, status)

    def set_misc_status(self, status):
        self.set_light_status(self.MISC_LIGHT, status)

    def set_process_status(self, status):
        if status == 0:
            self.set_light(self.PROCESS_LIGHT, Color(0, 0, 0))

        if status == 1:
            self.set_light(self.PROCESS_LIGHT, Color(0, 0, 255))

    def clear(self):
        for pin in [self.PROGRAM_LIGHT, self.GPS_LIGHT, self.WIFI_LIGHT, self.PROCESS_LIGHT, self.MISC_LIGHT]:
            self.set_light_status(pin, 0)