from pydantic import BaseModel
from enum import Enum

class BunkStatus(str, Enum):
	available = "available"
	busy = "busy"
	not_available = "not_available"


class BunkModel(BaseModel):
	bunk_number: int
	dispensary_id: int
	room_number: int

class BunkResponse(BaseModel):
	id: int
	bunk_status: BunkStatus = "available"
	bunk_number: int
	dispensary_id: int
	room_number: int

class BunkResponseForPost(BaseModel):
	result: str = "Bunk Added"
	id: int
	bunk_status: BunkStatus = "available"
	bunk_number: int
	dispensary_id: int
	room_number: int

class AllBunks(BaseModel):
	Bunks: list[BunkResponse]

