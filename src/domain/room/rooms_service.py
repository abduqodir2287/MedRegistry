from fastapi import Query, HTTPException, status, Depends

from src.domain.room.schema import AllRooms, RoomModel, RoomResponseForGet, RoomResponseForPost
from src.configs.logger_setup import logger
from src.domain.room.functions import RoomsFunctions
from src.infrastructure.database.postgres.create_db import room, dispensary
from src.domain.authorization.auth import get_token
from src.domain.authorization.dependencies import check_user_is_doctor


class RoomsService(RoomsFunctions):
	def __init__(self) -> None:
		super().__init__()


	async def get_rooms_service(self) -> AllRooms:
		all_rooms = await self.get_rooms_function()
		logger.info("Rooms sent from DB")

		return AllRooms(Rooms=all_rooms)


	async def add_room_service(
			self, room_number: int = Query(..., description="The number of the room"),
			dispensary_id: int = Query(..., description="The dispensary id of the room"),
			token: str = Depends(get_token)
	) -> RoomResponseForPost:
		room_model = RoomModel(
			room_number=room_number,
			dispensary_id=dispensary_id
		)
		await check_user_is_doctor(dispensary_id, token)

		exist_dispensary = await dispensary.dispensary_exists(dispensary_id)
		if not exist_dispensary:
			logger.warning("Dispensary not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no Dispensary with this id")

		if not await dispensary.select_dispensary_status(dispensary_id):
			logger.warning("Dispensary status is False")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This dispensary is not active right now")

		existing_room = await room.check_room_exists(room_number, dispensary_id)
		if existing_room:
			logger.warning("Room already added")
			raise HTTPException(
				status_code=status.HTTP_409_CONFLICT,
				detail="The Room with this number with this Dispensary already exists"
			)

		room_id = await room.insert_room(room_model)
		logger.info("Room added successfully")

		return RoomResponseForPost(RoomId=room_id)


	async def get_room_by_number_service(self, dispensary_id: int, room_number: int) -> RoomResponseForGet:
		dispensary_by_id = await self.get_room_by_id_function(dispensary_id, room_number)

		return dispensary_by_id

