from typing import Optional
from fastapi import Query, HTTPException, status, Response, Depends, Request

from src.configs.logger_setup import logger
from src.domain.users.functions import UsersFunctions
from src.domain.users.schema import UserModel, UserResponse, AllUsers, AuthorizedUser
from src.domain.users.schema import UserResponseForPut, UserResponseForPost
from src.domain.enums import UserRole
from src.infrastructure.database.postgres.create_db import dispensary, users
from src.domain.authorization.auth import create_access_token, get_token
from src.domain.authorization.dependencies import check_user_is_superadmin, check_user_is_doctor


class UsersService(UsersFunctions):

	def __init__(self):
		super().__init__()


	async def get_all_users_service(
			self, firstname: Optional[str] = None,
			lastname: Optional[str] = None,
			role: Optional[UserRole] = None,
			dispensary_id: Optional[int] = None
	) -> AllUsers:
		users_list = await self.get_all_users_function(firstname, lastname, role, dispensary_id)
		logger.info("Users sent from Db")

		return AllUsers(Users=users_list)


	@staticmethod
	async def auth_user(response: Response,
	                    firstname: str, lastname: str, password: str, dispensary_id: int) -> AuthorizedUser:

		user_by_name = await users.select_user_by_name(
			firstname.capitalize(), lastname.capitalize(), dispensary_id
		)

		if user_by_name is None:
			logger.warning("User not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

		if user_by_name.password != password:
			logger.warning("Incorrect password")
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You entered the wrong password")

		access_token = create_access_token({"sub": str(user_by_name.id)})
		response.set_cookie(key="user_access_token", value=access_token, httponly=True)

		logger.info("User is successfully authorized")

		return AuthorizedUser(result="User is successfully authorized")

	@staticmethod
	async def add_user_service(
			firstname: str = Query(..., description="The firstname of the bunk"),
			lastname: str = Query(..., description="The lastname of the user"),
			password: str = Query(..., description="Password for security"),
			job_title: Optional[str] = Query(None, description="The job title of the user"),
			dispensary_id: int = Query(..., description="The dispensary id of the bunk"),
			token: str = Depends(get_token)
	) -> UserResponseForPost:

		await check_user_is_doctor(dispensary_id, token)

		exist_dispensary = await dispensary.dispensary_exists(dispensary_id)
		if not exist_dispensary:
			logger.warning("Dispensary not found")
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="There is no Dispensary with this id."
			)

		if not await dispensary.select_dispensary_status(dispensary_id):
			logger.warning("Dispensary status is False")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This dispensary is not active right now")

		if len(password) < 6:
			logger.warning("Invalid password")
			raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			                    detail="The password must be at least 6 characters long.")

		user_model = UserModel(
			firstname=firstname,
			lastname=lastname,
			password=password,
			job_title=job_title,
			dispensary_id=dispensary_id
		)

		user_id = await users.insert_user(user_model)

		logger.info("User added successfully")

		return UserResponseForPost(UserId=user_id)


	@staticmethod
	async def delete_user_by_id_service(user_id: int, token: str = Query(get_token)) -> None:
		await check_user_is_superadmin(token)

		user_delete = await users.delete_user_by_id(user_id)

		if user_delete is None:
			logger.warning("User not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

		logger.info("User deleted successfully")


	async def get_user_by_id_service(self, user_id: int) -> UserResponse:
		user_by_id = await self.get_user_by_id_function(user_id)

		return user_by_id


	@staticmethod
	async def update_user_role_service(
			user_id: int, role: UserRole, token: str = Depends(get_token)) -> UserResponseForPut:
		await check_user_is_superadmin(token)

		user_by_id = await users.select_user_by_id(user_id)

		if user_by_id is None:
			logger.warning("User not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

		if await users.update_user_role(user_id, role):

			return UserResponseForPut(
				result="User Role updated",
				id=user_id,
				firstname=user_by_id.firstname,
				lastname=user_by_id.lastname,
				job_title=user_by_id.job_title,
				role=role,
				dispensary_id=user_by_id.dispensary_id
			)


	@staticmethod
	async def logout_service(request: Request, response: Response) -> None:
		access_token = request.cookies.get("user_access_token")

		if not access_token:
			logger.warning("Token not found")
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized")

		response.delete_cookie(key="user_access_token")

		logger.info("User logged out successfully")


