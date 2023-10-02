from typing import Any
import redis
import json

class CacheService:
    def __init__(self, host: str, port: int) -> None:
        self.redis_client = redis.Redis(host, port, db=0)
        # Set the maximum memory limit (in bytes)
        max_memory_bytes = 1024 * 1024 * 100 # 100MB
        self.redis_client.config_set('maxmemory', max_memory_bytes)
        # allkeys-lfu: Keeps frequently used keys; removes least frequently used (LFU) keys
        self.redis_client.config_set('maxmemory-policy', 'allkeys-lru')
        
    def cache(self, key: str, value: Any) -> None:
        json_string = json.dumps(value)
        self.redis_client.set(key, json_string)
        
    def get(self, key: str) -> None | Any:
        value_byte = self.redis_client.get(key)
        if value_byte is None:
            return
        return json.loads(value_byte.decode())
    
cache_service = CacheService("redis_cacher", 6379)