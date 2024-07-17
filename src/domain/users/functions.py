from src.domain.users.schema import UserResponse, UserModel, UserResponseForPost
from src.infrastructure.database.postgres.create_db import users

class UsersFunctions:

	def __init__(self):
		pass

	@staticmethod
	async def add_id_function(id: int, user_model: UserModel) -> UserResponseForPost:
		return UserResponseForPost(
			id=id,
			firstname=user_model.firstname,
			lastname=user_model.lastname,
			job_title=user_model.job_title,
			dispensary_id=user_model.dispensary_id
		)

	@staticmethod
	async def get_all_users_function() -> list:
		all_users = await users.select_all_users()
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



