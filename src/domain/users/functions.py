from typing import Optional

from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
import json


from src.configs.logger_setup import logger
from src.domain.users.schema import UserResponse, UserModel
from src.domain.enums import UserRole
from src.infrastructure.database.postgres.create_db import users
from src.infrastructure.database.redis.client import RedisClient
from src.configs.config import settings

class UsersFunctions:

	def __init__(self) -> None:
		self.redis_client = RedisClient(settings.REDIS_USERS)


	@staticmethod
	async def get_all_users_function(
			firstname: Optional[str] = None,
			lastname: Optional[str] = None,
			role: Optional[UserRole] = None,
			dispensary_id: Optional[int] = None
	) -> list:
		all_users = await users.select_users_like(firstname, lastname, role, dispensary_id)
		users_list = []

		for user in all_users:
			returned_users = UserResponse(
				id=user.id,
				firstname=user.firstname,
				lastname=user.lastname,
				job_title=user.job_title,
				role=user.role,
				dispensary_id=user.dispensary_id
			)

			users_list.append(returned_users)

		return users_list


	async def add_user_in_redis(self, user_id: int, user_model: UserModel) -> None:
		model_user = UserResponse(
			id=user_id,
			firstname=user_model.firstname,
			lastname=user_model.lastname,
			job_title=user_model.job_title,
			dispensary_id=user_model.dispensary_id
		)

		self.redis_client.set(user_id, json.dumps(jsonable_encoder(model_user)))


	async def get_all_users_redis(self) -> list:
		keys = self.redis_client.get_keys()
		users_list = []

		for key in keys:
			returned_users = self.redis_client.get(key)

			users_list.append(json.loads(returned_users))

		logger.info("User sent from Redis")
		return users_list


	@staticmethod
	async def get_user_by_id_function(user_id: int) -> UserResponse:
		user_by_id = await users.select_user_by_id(user_id)

		if user_by_id is None:
			logger.warning("User not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

		return UserResponse(
			id=user_by_id.id,
			firstname=user_by_id.firstname,
			lastname=user_by_id.lastname,
			job_title=user_by_id.job_title,
			role=user_by_id.role,
			dispensary_id=user_by_id.dispensary_id
		)


	async def get_user_by_id_redis(self, user_id: int) -> UserResponse:
		user_by_id = self.redis_client.get(user_id)

		if user_by_id is None:
			logger.warning("User not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this id not found")

		logger.info("User sent from Redis")
		return json.loads(user_by_id)


	async def update_user_role_redis(
			self, id: int, firstname: str, lastname: str,
			job_title: str, role: UserRole, dispensary_id: int
	) -> None:
		user_model = UserResponse(
			id=id,
			firstname=firstname,
			lastname=lastname,
			job_title=job_title,
			role=role,
			dispensary_id=dispensary_id
		)

		self.redis_client.set(id, json.dumps(jsonable_encoder(user_model)))

