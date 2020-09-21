import datetime


class CollectorCache:
    ADDS_PER_CLEAN = 100
    count_adds = 0

    cache = {}

    def add_to_cache(self, key, seconds_timeout):
        self.cache[key] = datetime.datetime.now() + datetime.timedelta(seconds=seconds_timeout)
        self.count_adds += 1
        if self.count_adds == self.ADDS_PER_CLEAN:
            self.clean()

    def is_in_cache(self, key):
        if key not in self.cache:
            return False

        if self.cache[key] < datetime.datetime.now():
            #   key is in the cache, but it has expired. Remove from cache.
            del self.cache[key]
            return False

        return key

    def clean(self):
        for key, value in self.cache.items():
            if value < datetime.datetime.now():
                del self.cache[key]
        self.count_adds = 0
