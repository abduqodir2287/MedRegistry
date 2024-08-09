import json
from typing import Optional

from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status

from src.configs.logger_setup import logger
from src.domain.bunk.schema import BunkResponse
from src.infrastructure.database.postgres.create_db import room, bunk
from src.domain.room.schema import RoomResponse, RoomModel, RoomResponseForGet
from src.domain.enums import RoomStatus
from src.infrastructure.database.redis.client import RedisClient
from src.configs.config import settings


class RoomsFunctions:

	def __init__(self):
		self.redis_client = RedisClient(settings.REDIS_ROOM)


	async def get_rooms_function(
			self, room_status: Optional[RoomStatus] = None,
			dispensary_id: Optional[int] = None
	) -> list[RoomResponseForGet]:
		rooms_list = []

		for rooms in await room.select_room_like(room_status, dispensary_id):
			returned_room = RoomResponseForGet(
				id=rooms.id,
				room_status=rooms.room_status,
				room_number=rooms.room_number,
				dispensary_id=rooms.dispensary_id,
				bunks=await self.get_bunk_by_room_number(rooms.dispensary_id, rooms.room_number)
			)

			rooms_list.append(returned_room)

		return rooms_list


	@staticmethod
	async def get_bunk_by_room_number(dispensary_id: int, room_number: int) -> list[BunkResponse]:
		all_bunks = await bunk.select_bunks_by_room_number(dispensary_id, room_number)
		bunks_list = []

		if all_bunks is not None:
			for b in all_bunks:
				if b is not None:
					returned_bunk = BunkResponse(
						id=b.id,
						bunk_status=b.bunk_status,
						bunk_number=b.bunk_number,
						room_number=room_number,
						dispensary_id=dispensary_id
					)

					bunks_list.append(returned_bunk)

		return bunks_list


	async def get_rooms_redis(self) -> list:
		keys = self.redis_client.get_keys()
		rooms_list = []

		for key in keys:
			returned_room = self.redis_client.get(key)

			rooms_list.append(json.loads(returned_room))

		return rooms_list


	async def add_room_redis(self, room_id: int, room_model: RoomModel) -> None:
		model_room = RoomResponse(
			id=room_id,
			room_number=room_model.room_number,
			dispensary_id=room_model.dispensary_id
		)

		self.redis_client.set(room_id, json.dumps(jsonable_encoder(model_room)))


	async def get_room_by_id_function(self, dispensary_id: int, room_number: int) -> RoomResponseForGet:
		room_by_number = await room.select_room_by_number(room_number, dispensary_id)

		if room_by_number is None:
			logger.warning("Room not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

		bunks_list = await self.get_bunk_by_room_number(dispensary_id, room_number)

		return RoomResponseForGet(
			id=room_by_number.id,
			room_status=room_by_number.room_status,
			room_number=room_number,
			dispensary_id=dispensary_id,
			bunks=bunks_list
		)


	async def update_room_status_redis(
			self, room_id: int, room_status: RoomStatus,
			room_number: int, dispensary_id: int
	) -> None:

		room_model = RoomResponse(
			id=room_id,
			room_status=room_status,
			room_number=room_number,
			dispensary_id=dispensary_id
		)

		self.redis_client.set(room_id, json.dumps(jsonable_encoder(room_model)))



