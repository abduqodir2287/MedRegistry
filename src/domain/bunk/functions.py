from fastapi import HTTPException, status

from src.configs.logger_setup import logger
from src.infrastructure.database.postgres.create_db import bunk, room
from src.domain.bunk.schema import BunkResponse, BunkModel, BunkResponseForPost


class BunkFunctions:

	def __init__(self):
		pass

	async def get_bunks_function(self) -> list:
		bunks_list = []
		for bunks in await bunk.select_all_bunks():
			returned_bunks = BunkResponse(
				id=bunks.id,
				bunk_status=bunks.bunk_status,
				bunk_number=bunks.bunk_number,
				dispensary_id=bunks.dispensary_id,
				room_number=bunks.room_number
			)
			bunks_list.append(returned_bunks)

		return bunks_list


	async def add_id_function(self, id: int, bunk_model: BunkModel) -> BunkResponseForPost:
		return BunkResponseForPost(
			id=id,
			bunk_number=bunk_model.bunk_number,
			dispensary_id=bunk_model.dispensary_id,
			room_number=bunk_model.room_number
		)


	async def check_bunk(self, dispensary_id: int, room_number: int, bunk_number: int) -> bool:
		check = await bunk.select_bunk_by_number(dispensary_id, room_number, bunk_number)

		if check:
			logger.warning("Bunk already added")
			raise HTTPException(
				status_code=status.HTTP_409_CONFLICT,
				detail="Bunk with this number in this room already exists in this dispensary"
			)

		return True


	async def check_room(self, room_number: int, dispensary_id: int) -> bool:
		exist_room = await room.room_exists(room_number)
		room_by_number = await room.select_room_by_number(room_number, dispensary_id)

		if not exist_room:
			logger.warning("Room not found")
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="There is no Room with this id."
			)

		if room_by_number.dispensary_id != dispensary_id:
			logger.warning("This Room is not located in this Dispensary")
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="This Room is not located in this Dispensary"
			)

		return True


