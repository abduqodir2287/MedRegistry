from pydantic import BaseModel
from enum import Enum

class RoomStatus(Enum):
	available = "available"
	busy = "busy"
	not_available = "not_available"


class RoomModel(BaseModel):
	room_status: RoomStatus
	room_number: int
	dispensary_id: int
