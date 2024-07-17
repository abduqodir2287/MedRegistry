from fastapi import Query, HTTPException, status

from src.domain.room.schema import AllRooms, RoomStatus, RoomResponseForPost, RoomModel, RoomResponse
from src.configs.logger_setup import logger
from src.domain.room.functions import RoomsFunctions
from src.infrastructure.database.postgres.create_db import room, dispensary


class RoomsService(RoomsFunctions):
	def __init__(self) -> None:
		super().__init__()


	async def get_rooms_service(self) -> AllRooms:
		all_rooms = await self.get_rooms_function()
		logger.info("Rooms sent from DB")

		return AllRooms(Rooms=all_rooms)

	async def add_room_service(
			self, room_number: int = Query(..., description="The number of the room"),
			dispensary_id: int = Query(..., description="The dispensary id of the room")
	) -> RoomResponseForPost:
		room_model = RoomModel(
			room_number=room_number,
			dispensary_id=dispensary_id
		)

		exist_dispensary = await dispensary.dispensary_exists(dispensary_id)
		if not exist_dispensary:
			logger.warning("Dispensary not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no Dispensary with this id")

		existing_room = await room.check_room_exists(room_number, dispensary_id)
		if existing_room:
			logger.warning("Room already added")
			raise HTTPException(
				status_code=status.HTTP_409_CONFLICT,
				detail="The Room with this number with this Dispensary already exists"
			)

		insert_response = await room.insert_room(room_model)

		result = await self.add_id_function(insert_response, room_model)
		logger.info("Room added successfully")

		return result


	async def get_room_by_number_service(self, dispensary_id: int, room_number: int) -> RoomResponse:
		room_by_number = await room.select_room_by_number(room_number, dispensary_id)

		if room_by_number is None:
			logger.warning("Room not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

		return RoomResponse(
			id=room_by_number.id,
			room_status=room_by_number.room_status,
			room_number=room_number,
			dispensary_id=dispensary_id
		)


	async def delete_room_by_id_service(self, room_id: int) -> None:
		result = await room.delete_room_by_id(room_id)

		if result is None:
			logger.warning("Room not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

		logger.info("Room deleted successfully")


	async def update_room_status_by_id_service(self, room_id: int, room_status: RoomStatus) -> RoomResponseForPost:
		room_by_id = await room.select_room_by_id(room_id)

		if room_by_id is None:
			logger.warning("Room not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

		await room.update_room_by_id(room_id, room_status)

		return RoomResponseForPost(
			result="Room Updated",
			id=room_id,
			room_status=room_status,
			room_number=room_by_id.room_number,
			dispensary_id=room_by_id.dispensary_id
		)





