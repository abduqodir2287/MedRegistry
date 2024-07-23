from redis import Redis

from src.configs.config import settings


class RedisClient:
	def __init__(self, redis_database: int):
		self.redis_client = Redis(
			host=settings.REDIS_HOST, port=settings.REDIS_PORT,
			db=redis_database, decode_responses="utf-8"
		)

	def set_with_ttl(self, key: str | int, data: dict) -> None:
		self.redis_client.hset(key, mapping=data)
		self.redis_client.expire(key, settings.REDIS_CACHE_EXPIRATION)


	def set(self, key: str | int, data: str) -> None:
		self.redis_client.set(key, data)


	def get_dict(self, key: str | int) -> dict:
		if self.redis_client.exists(key):
			return self.redis_client.hgetall(key)


	def get(self, key: str | int) -> str:
		if self.redis_client.exists(key):
			return self.redis_client.get(key)


	def get_keys(self) -> list:
		return self.redis_client.keys("*")


	def delete(self, key: str | int) -> None:
		self.redis_client.delete(key)


	def exist(self, key: str | int) -> bool | None:
		if self.redis_client.exists(key):
			return True


