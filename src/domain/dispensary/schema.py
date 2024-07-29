from pydantic import BaseModel

from src.domain.bunk.schema import BunkResponse
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


class DispensaryWithAvailableBunks(BaseModel):
	id: int
	dispensary_name: str
	address: str
	active: bool
	free_bunks: list[BunkResponse]

class DispensaryPutModel(BaseModel):
	result: str = "Dispensary updated"
	id: int
	dispensary_name: str
	address: str


class DispensaryResponseForPost(BaseModel):
	DispensaryID: int


class DispensaryResponseForPut(BaseModel):
	result: str = "Dispensary updated"
	id: int
	dispensary_name: str
	address: str
	active: bool = True


class AllDispensaries(BaseModel):
	Dispensaries: list[DispensaryResponseForGet]


