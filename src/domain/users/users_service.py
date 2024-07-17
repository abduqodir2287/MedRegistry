from typing import Optional
from fastapi import Query, HTTPException, status

from src.configs.logger_setup import logger
from src.domain.users.functions import UsersFunctions
from src.domain.users.schema import UserModel, UserResponse, AllUsers, UserRole, UserResponseForPost
from src.infrastructure.database.postgres.create_db import dispensary, users


class UsersService(UsersFunctions):

	def __init__(self):
		super().__init__()


	async def get_all_users_service(self) -> AllUsers:
		users_list = await self.get_all_users_function()

		return AllUsers(Users=users_list)


	async def add_user_service(
			self, firstname: str = Query(..., description="The firstname of the bunk"),
			lastname: str = Query(..., description="The lastname of the user"),
			job_title: Optional[str] = Query(None, description="The job title of the user"),
			dispensary_id: int = Query(..., description="The dispensary id of the bunk")
	) -> UserResponseForPost:

		user_model = UserModel(
			firstname=firstname,
			lastname=lastname,
			job_title=job_title,
			dispensary_id=dispensary_id
		)

		exist_dispensary = await dispensary.dispensary_exists(dispensary_id)
		if not exist_dispensary:
			logger.warning("Dispensary not found")
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="There is no Dispensary with this id."
			)

		user_id = await users.insert_user(user_model)

		result = await self.add_id_function(user_id, user_model)
		logger.info("User added successfully")

		return result


	async def delete_user_by_id_service(self, user_id: int) -> None:
		user_delete = await users.delete_user_by_id(user_id)

		if user_delete is None:
			logger.warning("User not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

		logger.info("User deleted successfully")


	async def get_user_by_id_service(self, user_id: int) -> UserResponse:
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


	async def update_role_user_service(self, user_id: int, role: UserRole) -> UserResponseForPost:
		user_by_id = await users.select_user_by_id(user_id)

		if user_by_id is None:
			logger.warning("User not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

		if await users.update_user_role(user_id, role):

			return UserResponseForPost(
				result="User Role updated",
				id=user_id,
				firstname=user_by_id.firstname,
				lastname=user_by_id.lastname,
				job_title=user_by_id.job_title,
				role=role,
				dispensary_id=user_by_id.dispensary_id
			)



