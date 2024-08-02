from typing import Optional

from fastapi import APIRouter, Query, status, Response, Depends

from src.domain.authorization.auth import get_token
from src.domain.users.schema import UserResponse, AllUsers, UserResponseForPut, UserResponseForPost
from src.domain.enums import UserRole
from src.domain.users.schema import AuthorizedUser
from src.domain.users.users_service import UsersService

users_router = APIRouter(prefix="/Users", tags=["Users"])

users_service = UsersService()


@users_router.get("", response_model=AllUsers, status_code=status.HTTP_200_OK)
async def get_all_users(
		firstname: Optional[str] = Query(None, description="The firstname of the User"),
		lastname: Optional[str] = Query(None, description="The lastname of the User"),
		role: UserRole = Query(None, description="The role of the User"),
		dispensary_id: Optional[int] = Query(None, description="The dispensary_id of the User")
) -> AllUsers:
	return await users_service.get_all_users_service(firstname, lastname, role, dispensary_id)


@users_router.post("/authorization", response_model=AuthorizedUser, status_code=status.HTTP_200_OK)
async def user_authorization(
		response: Response, firstname: str = Query(..., description="The firstname of the user"),
		lastname: str = Query(..., description="The lastname of the user"),
		password: str = Query(..., description="Password for security"),
		dispensary_id: int = Query(..., description="The dispensary id of the user")
) -> AuthorizedUser:
	return await users_service.auth_user(response, firstname, lastname, password, dispensary_id)


@users_router.post("", response_model=UserResponseForPost, status_code=status.HTTP_201_CREATED)
async def add_user(
		firstname: str = Query(..., description="The firstname of the bunk"),
		lastname: str = Query(..., description="The lastname of the user"),
		password: str = Query(..., description="Password for security"),
		job_title: Optional[str] = Query(None, description="The job title of the user"),
		dispensary_id: int = Query(..., description="The dispensary id of the bunk"),
		token: str = Depends(get_token)
) -> UserResponseForPost:
	return await users_service.add_user_service(firstname, lastname, password, job_title, dispensary_id, token)


@users_router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_by_id(user_id: int) -> UserResponse:
	return await users_service.get_user_by_id_service(user_id)


@users_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, token: str = Depends(get_token)) -> None:
	await users_service.delete_user_by_id_service(user_id, token)


@users_router.patch("/{user_id}", response_model=UserResponseForPut, status_code=status.HTTP_200_OK)
async def update_user_role(
		user_id: int, role: UserRole = Query(..., description="The role of the User"),
		token: str = Depends(get_token)
) -> UserResponseForPut:
	return await users_service.update_user_role_service(user_id, role, token)


@users_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(response: Response) -> None:
	response.delete_cookie(key="user_access_token")

