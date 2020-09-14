import os

import redis
from rq import Queue
import time

class RedisCache:
    q = None

    def __init__(self):
        ping = False
        while not ping:
            try:
                ping = self.get_connection().ping()
                print(ping)
            except:
                pass
            time.sleep(1)

    def get_connection(self):
        return redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))

    def get_row(self, statement):
        redis_result = self.get_connection().get(statement)
        if redis_result is not None:
            return redis_result.decode("utf-8")

    def set_key(self, key_name, value, timeout=0):
        if timeout == 0:
            timeout = 1
        self.get_connection().set(key_name, value, ex=timeout)

    def delete_key(self, key_name):
        self.get_connection().delete(key_name)

    def is_key_in_store(self, key):
        redis_result = self.get_connection().get(key)
        return redis_result is not None

    def get_job_queue(self):
        if self.q is None:
            self.q = Queue(connection=self.get_connection())
        return self.q

    def enqueue_job(self, method, arguments, timeout=500):
        return self.get_job_queue().enqueue_call(method, args=arguments, result_ttl=timeout)


if __name__ == '__main__':
    x = RedisCache().get_connection()
    print(x)