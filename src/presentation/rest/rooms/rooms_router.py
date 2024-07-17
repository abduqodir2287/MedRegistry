from fastapi import APIRouter, status, Query

from src.domain.room.rooms_service import RoomsService
from src.domain.room.schema import AllRooms, RoomResponseForPost, RoomStatus, RoomResponse


room_router = APIRouter(prefix="/Room", tags=["Rooms"])

room_service = RoomsService()


@room_router.get("", response_model=AllRooms, status_code=status.HTTP_200_OK)
async def get_rooms() -> AllRooms:
	return await room_service.get_rooms_service()


@room_router.post("", response_model=RoomResponseForPost, status_code=status.HTTP_200_OK)
async def add_rooms(
		room_number: int = Query(..., description="The number of the room"),
		dispensary_id: int = Query(..., description="The dispensary id of the room")
) -> RoomResponseForPost:
	return await room_service.add_room_service(room_number, dispensary_id)


@room_router.get("/dispensary_id/room_number", response_model=RoomResponse, status_code=status.HTTP_200_OK)
async def get_room_by_number(dispensary_id: int, room_number: int) -> RoomResponse:
	return await room_service.get_room_by_number_service(dispensary_id, room_number)


@room_router.delete("/room_id", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dispensary(room_id: int) -> None:
	return await room_service.delete_room_by_id_service(room_id)


@room_router.patch("/room_id", response_model=RoomResponseForPost, status_code=status.HTTP_200_OK)
async def update_dispensary(
		room_id: int, room_status: RoomStatus = Query(..., description="The status of the Room")
) -> RoomResponseForPost:
	return await room_service.update_room_status_by_id_service(room_id, room_status)

