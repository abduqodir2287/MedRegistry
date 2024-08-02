from typing import Optional
from pydantic import BaseModel

from src.domain.enums import UserRole


class UserModel(BaseModel):
	firstname: str
	lastname: str
	password: str
	job_title: Optional[str] = None
	dispensary_id: int


class UserResponse(BaseModel):
	id: int
	firstname: str
	lastname: str
	job_title: Optional[str] = None
	role: UserRole = UserRole.user
	dispensary_id: int

class UserResponseForPut(BaseModel):
	result: str = "User added"
	id: int
	firstname: str
	lastname: str
	job_title: Optional[str] = None
	role: UserRole = UserRole.user
	dispensary_id: int

class UserResponseForPost(BaseModel):
	UserId: int


class AuthorizedUser(BaseModel):
	result: str


class AllUsers(BaseModel):
	Users: list[UserResponse]


