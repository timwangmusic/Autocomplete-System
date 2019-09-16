"""
    Redis manager is responsible for managing Redis connections and various IO operations
    from the autocomplete server to one Redis server.
"""
import redis


class RedisManager:
    def __init__(self, redis_host: str, redis_port: str, db_idx: int):
        # decode_responses equals True makes sure the response is composed of strings instead of bytes
        self.redis_client = redis.Redis(redis_host, redis_port, db_idx, decode_responses=True)

    # save search results as Redis list
    def cache_search_results(self, search_term: str, search_results: list) -> None:
        self.redis_client.rpush(search_term, *search_results)

    # retrieve search results from Redis
    def get_search_results(self, search_term: str) -> list:
        return self.redis_client.lrange(search_term, 0, -1)
