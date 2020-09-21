import datetime


class CollectorCache:
    ADDS_PER_CLEAN = 10
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
        keys_to_delete = [key for key, value in self.cache.items() if value < datetime.datetime.now()]
        print("removing %s keys, %s remain" % (len(keys_to_delete), len(self.cache) - len(keys_to_delete)))
        for key in keys_to_delete:
            del self.cache[key]

        self.count_adds = 0
