from typing import Optional

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
import json

from src.configs.logger_setup import logger
from src.domain.bunk.schema import BunkResponse
from src.domain.dispensary.schema import DispensaryResponse, DispensaryPutModel, DispensaryResponseForGet
from src.domain.room.schema import RoomResponse
from src.infrastructure.database.postgres.create_db import dispensary, room, bunk
from src.domain.dispensary.schema import DispensaryModel
from src.infrastructure.database.redis.client import RedisClient
from src.configs.config import settings


class DispensariesFunctions:

	def __init__(self):
		self.redis_client = RedisClient(settings.REDIS_DISPENSARY)


	@staticmethod
	async def get_rooms_by_dispensary_id_function(dispensary_id: int) -> list[RoomResponse]:
		room_by_dispensary_id = await room.get_rooms_by_dispensary_id(dispensary_id)
		rooms_list = []

		if room_by_dispensary_id is not None:
			for r in room_by_dispensary_id:
				if r is not None:

					returned_room = RoomResponse(
							id=r.id, room_status=r.room_status,
							room_number=r.room_number, dispensary_id=dispensary_id
						)

					rooms_list.append(returned_room)

		return rooms_list


	async def get_all_dispensaries(
			self, dispensary_id: Optional[int] = None,
			dispensary_name: Optional[str] = None,
			address: Optional[str] = None
	) -> list[DispensaryResponseForGet]:
		dispensaries = await dispensary.select_dispensary_like(dispensary_id, dispensary_name, address)
		dispensary_list = []

		for d in dispensaries:
			rooms_list = await self.get_rooms_by_dispensary_id_function(d.id)

			all_dispensaries = DispensaryResponseForGet(
				id=d.id,
				dispensary_name=d.dispensary_name,
				address=d.address,
				active=d.active,
				rooms=rooms_list,
				free_bunks=await bunk.free_bunks_by_dispensary_id(d.id)
			)

			dispensary_list.append(all_dispensaries)

		return dispensary_list


	async def get_dispensaries_redis_function(self) -> list:
		dispensaries_list = []
		keys = self.redis_client.get_keys()

		for key in keys:
			returned_dispensary = self.redis_client.get(key)
			dispensaries_list.append(json.loads(returned_dispensary))

		return dispensaries_list


	async def get_dispensary_by_id_function(self, id: int) -> DispensaryResponseForGet:
		dispensary_by_id = await dispensary.select_dispensary_by_id(id)

		if dispensary_by_id is None:
			logger.warning("Dispensary not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispensary not found")

		all_rooms = await self.get_rooms_by_dispensary_id_function(dispensary_by_id.id)

		logger.info("Dispensary sent successfully")
		return DispensaryResponseForGet(
			id=id,
			dispensary_name=dispensary_by_id.dispensary_name,
			address=dispensary_by_id.address,
			active=dispensary_by_id.active,
			rooms=all_rooms,
			free_bunks=await bunk.free_bunks_by_dispensary_id(dispensary_by_id.id)
		)

	@staticmethod
	async def get_bunk_by_dispensary_id(dispensary_id: int) -> list[BunkResponse]:
		all_bunks = await bunk.select_available_bunks_by_id(dispensary_id)
		bunks_list = []

		if all_bunks is not None:
			for b in all_bunks:
				if b is not None:
					returned_bunk = BunkResponse(
						id=b.id,
						bunk_status=b.bunk_status,
						bunk_number=b.bunk_number,
						room_number=b.room_number,
						dispensary_id=dispensary_id
					)

					bunks_list.append(returned_bunk)

		return bunks_list


	async def get_dispensary_by_id_redis(self, dispensary_id: int) -> DispensaryResponse:
		dispensary_by_id = self.redis_client.get(dispensary_id)

		if dispensary_by_id is None:

			logger.warning("Dispensary not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispensary not found")

		result = json.loads(dispensary_by_id)
		logger.info("Dispensary sent from Redis")

		return result


	async def add_dispensary_in_cache(self, dispensary_id: int, dispensary_model: DispensaryModel) -> None:
		model_dispensary = DispensaryResponse(
			id=dispensary_id,
			dispensary_name=dispensary_model.dispensary_name,
			address=dispensary_model.address
		)

		self.redis_client.set(dispensary_id, json.dumps(jsonable_encoder(model_dispensary)))


	@staticmethod
	async def update_response_function(id: int, dis_model: DispensaryModel) -> DispensaryPutModel:
		return DispensaryPutModel(
			result="Dispensary updated",
			id=id,
			dispensary_name=dis_model.dispensary_name,
			address=dis_model.address
		)

	async def update_dispensary_in_cache(self, id: int, dispensary_model: DispensaryModel) -> None:
		if self.redis_client.exist(id):
			dispensary_by_id = DispensaryResponse(
				id=id,
				dispensary_name=dispensary_model.dispensary_name,
				address=dispensary_model.address
			)
			self.redis_client.set(id, json.dumps(jsonable_encoder(dispensary_by_id)))





