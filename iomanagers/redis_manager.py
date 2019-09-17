"""
    Redis manager is responsible for managing Redis connections and various IO operations
    from the autocomplete server to one Redis server.
"""
import redis


class RedisManager:
    def __init__(self, redis_host: str = 'localhost', redis_port: str = '6379', db_idx: int = 0):
        # decode_responses equals True makes sure the response is composed of strings instead of bytes
        self.redis_client = redis.Redis(redis_host, redis_port, db_idx, decode_responses=True)

    # save search results as Redis list
    def cache_search_results(self, search_term: str, search_results: list) -> None:
        redis_key = "search_term:" + search_term
        self.redis_client.rpush(redis_key, *search_results)

    # retrieve search results from Redis
    def get_search_results(self, search_term: str) -> list:
        redis_key = "search_term:" + search_term
        return self.redis_client.lrange(redis_key, 0, -1)
