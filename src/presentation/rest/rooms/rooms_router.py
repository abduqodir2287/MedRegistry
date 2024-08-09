from typing import Optional
from fastapi import APIRouter, status, Query, Depends

from src.domain.authorization.auth import get_token
from src.domain.enums import RoomStatus
from src.domain.room.rooms_service import RoomsService
from src.domain.room.schema import AllRooms, RoomResponseForGet, RoomResponseForPost

room_router = APIRouter(prefix="/Room", tags=["Rooms"])

room_service = RoomsService()


@room_router.get("", response_model=AllRooms, status_code=status.HTTP_200_OK)
async def get_rooms(
		room_status: RoomStatus = Query(None, description="The status of the Room"),
		dispensary_id: Optional[int] = Query(None, description="The dispensary_id of the Room")
) -> AllRooms:
	return await room_service.get_rooms_service(room_status, dispensary_id)


@room_router.post("", response_model=RoomResponseForPost, status_code=status.HTTP_201_CREATED)
async def add_rooms(
		room_number: int = Query(..., description="The number of the room"),
		dispensary_id: int = Query(..., description="The dispensary id of the room"),
		token: str = Depends(get_token)
) -> RoomResponseForPost:
	return await room_service.add_room_service(room_number, dispensary_id, token)


@room_router.get("/{dispensary_id}/{room_number}", response_model=RoomResponseForGet, status_code=status.HTTP_200_OK)
async def get_room_by_number(dispensary_id: int, room_number: int) -> RoomResponseForGet:
	return await room_service.get_room_by_number_service(dispensary_id, room_number)

