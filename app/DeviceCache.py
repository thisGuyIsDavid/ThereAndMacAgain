import datetime


class DeviceCache:
    LIMIT = 250
    MAX_TIME_IN_CACHE = 60
    cache = []

    def is_in_cache(self, mac_address):
        """
        :return:    False if address not in cache OR if address has not been seen for SECONDS_TO_IGNORE seconds.
                    True if address has been seen within SECONDS_TO_IGNORE seconds.
        """

        #   if the mac address is not in the cache, add the current time and return false
        cache_index = -1
        cache_entry = None

        for i, value in enumerate(self.cache):
            if value.get('mac_address') == mac_address:
                cache_entry = value
                cache_index = i

        if cache_entry is None:
            self.add_to_cache(mac_address)
            return False

        time_added = cache_entry.get('when_recorded')
        if (datetime.datetime.now() - time_added).seconds <= self.MAX_TIME_IN_CACHE:
            return True

        #   reset time seen
        self.cache.pop(cache_index)
        self.add_to_cache(mac_address)
        return False

    def add_to_cache(self, mac_address):
        self.cache.append({'mac_address': mac_address, 'when_recorded': datetime.datetime.now()})
        self.clean_cache()

    def clean_cache(self):
        if len(self.cache) < self.LIMIT:
            return
        to_pop = self.cache.pop(0)
        print('Popped address stayed for %s seconds' % (datetime.datetime.now() - to_pop.get('when_recorded')).seconds)