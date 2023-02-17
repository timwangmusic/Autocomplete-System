"""
    Redis manager is responsible for managing Redis connections and various IO operations
    from the autocomplete server to one Redis server.
"""
import redis


class RedisManager:
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379, db_idx: int = 0):
        # decode_responses equals True makes sure the response is composed of strings instead of bytes
        self.client = redis.Redis(redis_host, redis_port, db_idx, decode_responses=True)
        self.key_expiration_time = 3600

    # save search results as Redis list
    def cache_search_results(self, search_term: str, search_results: list) -> None:
        if search_results is None or len(search_results) == 0:
            return
        redis_key = "search_term:" + search_term
        self.client.rpush(redis_key, *search_results)
        self.client.expire(redis_key, self.key_expiration_time)

    # retrieve search results from Redis
    def get_search_results(self, search_term: str) -> list:
        redis_key = "search_term:" + search_term
        return self.client.lrange(redis_key, 0, -1)
