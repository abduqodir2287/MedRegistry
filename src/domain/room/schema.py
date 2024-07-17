from pydantic import BaseModel
from enum import Enum

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

class RoomResponseForPost(BaseModel):
	result: str = "Room added"
	id: int
	room_status: RoomStatus = "available"
	room_number: int
	dispensary_id: int

class AllRooms(BaseModel):
	Rooms: list[RoomResponse]

