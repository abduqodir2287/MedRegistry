from typing import Optional

from fastapi import APIRouter, Query, status

from src.domain.users.schema import UserResponse, AllUsers, UserResponseForPost, UserRole
from src.domain.users.users_service import UsersService

users_router = APIRouter(prefix="/Users", tags=["Users"])

users_service = UsersService()


@users_router.get("", response_model=AllUsers, status_code=status.HTTP_200_OK)
async def get_all_users() -> AllUsers:
	return await users_service.get_all_users_service()


@users_router.post("", response_model=UserResponseForPost, status_code=status.HTTP_200_OK)
async def add_user(
		firstname: str = Query(..., description="The firstname of the bunk"),
		lastname: str = Query(..., description="The lastname of the user"),
		job_title: Optional[str] = Query(None, description="The job title of the user"),
		dispensary_id: int = Query(..., description="The dispensary id of the bunk"),
) -> UserResponseForPost:
	return await users_service.add_user_service(firstname, lastname, job_title, dispensary_id)


@users_router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_by_id(user_id: int) -> UserResponse:
	return await users_service.get_user_by_id_service(user_id)


@users_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int) -> None:
	await users_service.delete_user_by_id_service(user_id)


@users_router.patch("/user_id/role", response_model=UserResponseForPost, status_code=status.HTTP_200_OK)
async def update_user_role(
		user_id: int, role: UserRole = Query(..., description="The role of the User")
) -> UserResponseForPost:
	return await users_service.update_user_role_service(user_id, role)


