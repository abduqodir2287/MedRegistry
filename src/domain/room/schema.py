from pydantic import BaseModel

from src.domain.bunk.schema import BunkResponse
from src.domain.enums import RoomStatus


class RoomModel(BaseModel):
	room_number: int
	dispensary_id: int

class RoomResponse(BaseModel):
	id: int
	room_status: RoomStatus = RoomStatus.available
	room_number: int
	dispensary_id: int


class RoomResponseForGet(BaseModel):
	id: int
	room_status: RoomStatus = RoomStatus.available
	room_number: int
	dispensary_id: int
	bunks: list[BunkResponse]


class RoomResponseForPost(BaseModel):
	RoomId: int


class RoomResponseForPut(BaseModel):
	result: str = "Room added"
	id: int
	room_status: RoomStatus = RoomStatus.available
	room_number: int
	dispensary_id: int

class AllRooms(BaseModel):
	Rooms: list[RoomResponseForGet]

