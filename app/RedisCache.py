import os
import datetime
import redis


class RedisCache:

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

    @staticmethod
    def flush():
        conn = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))
        conn.flushdb()
        conn.flushall()


if __name__ == '__main__':
    pass