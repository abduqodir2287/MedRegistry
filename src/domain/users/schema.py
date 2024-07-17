from typing import Optional

from pydantic import BaseModel
from enum import Enum

class UserRole(str, Enum):
	user = "user"
	doctor = "doctor"
	superadmin = "superadmin"


class UserModel(BaseModel):
	firstname: str
	lastname: str
	job_title: Optional[str] = None
	dispensary_id: int


class UserResponse(BaseModel):
	id: int
	firstname: str
	lastname: str
	job_title: Optional[str] = None
	role: UserRole = "user"
	dispensary_id: int

class UserResponseForPost(BaseModel):
	result: str = "User added"
	id: int
	firstname: str
	lastname: str
	job_title: Optional[str] = None
	role: UserRole = "user"
	dispensary_id: int


class AllUsers(BaseModel):
	Users: list[UserResponse]


