from pydantic import BaseModel

from src.domain.room.schema import RoomResponse

class DispensaryModel(BaseModel):
	dispensary_name: str
	address: str

class DispensaryResponse(BaseModel):
	id: int
	dispensary_name: str
	address: str
	active: bool = True

class DispensaryResponseForGet(BaseModel):
	id: int
	dispensary_name: str
	address: str
	active: bool
	rooms: list[RoomResponse]
	free_bunks: int | str

class DispensaryResponseForPost(BaseModel):
	result: str = "Task updated"
	id: int
	dispensary_name: str
	address: str

class DispensaryResponseForPut(BaseModel):
	result: str = "Task updated"
	id: int
	dispensary_name: str
	address: str
	active: bool = True


class AllDispensaries(BaseModel):
	Dispensaries: list[DispensaryResponseForGet]
