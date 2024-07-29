from pydantic import BaseModel
from enum import Enum

from src.domain.bunk.schema import BunkResponse


class RoomStatus(str, Enum):
	available = "available"
	busy = "busy"
	not_available = "not_available"


class RoomModel(BaseModel):
	room_number: int
	dispensary_id: int

class RoomResponse(BaseModel):
	id: int
	room_status: RoomStatus = "available"
	room_number: int
	dispensary_id: int


class RoomResponseForGet(BaseModel):
	id: int
	room_status: RoomStatus = "available"
	room_number: int
	dispensary_id: int
	bunks: list[BunkResponse]


class RoomResponseForPost(BaseModel):
	RoomId: int


class RoomResponseForPut(BaseModel):
	result: str = "Room added"
	id: int
	room_status: RoomStatus = "available"
	room_number: int
	dispensary_id: int

class AllRooms(BaseModel):
	Rooms: list[RoomResponseForGet]

