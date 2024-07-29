import json
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status

from src.configs.logger_setup import logger
from src.domain.patient.schema import PatientResponse
from src.infrastructure.database.postgres.create_db import bunk, room, patient
from src.domain.bunk.schema import BunkResponse, BunkModel, BunkStatus, BunkResponseForGet
from src.domain.room.schema import RoomStatus
from src.infrastructure.database.redis.client import RedisClient
from src.configs.config import settings


class BunkFunctions:

	def __init__(self):
		self.redis_client = RedisClient(settings.REDIS_BUNK)


	async def get_bunks_function(self) -> list[BunkResponseForGet]:
		bunks_list = []
		for bunks in await bunk.select_all_bunks():
			returned_bunks = BunkResponseForGet(
				id=bunks.id,
				bunk_status=bunks.bunk_status,
				dispensary_id=bunks.dispensary_id,
				room_number=bunks.room_number,
				bunk_number=bunks.bunk_number,
				patient=await self.get_patients_for_bunks(bunks.dispensary_id, bunks.room_number, bunks.bunk_number)
			)
			bunks_list.append(returned_bunks)

		logger.info("Bunks sent from DB")
		return bunks_list



	@staticmethod
	async def get_available_bunks_function() -> list[BunkResponse]:
		available_bunks = await bunk.select_available_bunks()
		bunks_list = []

		if available_bunks is None:
			logger.warning("Available bunks not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Available bunks not found")

		for b in available_bunks:
			returned_bunk = BunkResponse(
				id=b.id,
				bunk_status=b.bunk_status,
				dispensary_id=b.dispensary_id,
				room_number=b.room_number,
				bunk_number=b.bunk_number
			)

			bunks_list.append(returned_bunk)

		return bunks_list


	@staticmethod
	async def get_patients_for_bunks(dispensary_id: int, room_number: int, bunk_number: int) -> PatientResponse | None:
		patient_by_id = await patient.select_patient_by_bunk_number(dispensary_id, room_number, bunk_number)

		if patient_by_id is not None:

			return PatientResponse(
				id=patient_by_id.id,
				firstname=patient_by_id.firstname,
				lastname=patient_by_id.lastname,
				arrival_date=patient_by_id.arrival_date,
				status=patient_by_id.status,
				dispensary_id=dispensary_id,
				room_number=room_number,
				bunk_number=bunk_number
			)


	async def get_bunks_from_redis(self) -> list:
		keys = self.redis_client.get_keys()
		bunks_list = []

		for key in keys:
			returned_bunk = self.redis_client.get(key)

			bunks_list.append(json.loads(returned_bunk))

		return bunks_list


	async def add_bunk_redis(self, id: int, bunk_model: BunkModel) -> None:
		model_bunk = BunkResponse(
			id=id,
			room_number=bunk_model.room_number,
			dispensary_id=bunk_model.dispensary_id,
			bunk_number=bunk_model.bunk_number
		)

		self.redis_client.set(id, json.dumps(jsonable_encoder(model_bunk)))


	@staticmethod
	async def check_bunk(dispensary_id: int, room_number: int, bunk_number: int) -> bool:
		check = await bunk.select_bunk_by_number(dispensary_id, room_number, bunk_number)

		if check:
			logger.warning("Bunk already added")
			raise HTTPException(
				status_code=status.HTTP_409_CONFLICT,
				detail="Bunk with this number in this room already exists in this dispensary"
			)

		return True

	@staticmethod
	async def check_room(room_number: int, dispensary_id: int) -> bool | None:
		room_by_number = await room.select_room_by_number(room_number, dispensary_id)

		busy = RoomStatus("busy")
		not_available = RoomStatus("not_available")

		if room_by_number:
			if room_by_number.room_status == busy:
				logger.warning("Room already reserved")
				raise HTTPException(
					status_code=status.HTTP_404_NOT_FOUND,
					detail="Room already reserved"
				)

			if room_by_number.room_status == not_available:
				logger.warning("Room not available")
				raise HTTPException(
					status_code=status.HTTP_404_NOT_FOUND,
					detail="For some reason the Room is unavailable"
				)

			return True

		logger.warning("Room not found")
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="There is no Room with this id."
		)



	async def get_bunk_by_number_function(
			self, dispensary_id: int, room_number: int,
			bunk_number: int
	) -> BunkResponseForGet:
		bunk_by_number = await bunk.select_bunk_by_number(dispensary_id, room_number, bunk_number)

		if bunk_by_number is None:
			logger.warning("Bunk not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bunk not found")

		patient_by_number = await self.get_patients_for_bunks(dispensary_id, room_number, bunk_number)

		logger.info("Bunk sent from DB")

		return BunkResponseForGet(
			id=bunk_by_number.id,
			bunk_status=bunk_by_number.bunk_status,
			dispensary_id=dispensary_id,
			room_number=room_number,
			bunk_number=bunk_number,
			patient=patient_by_number
		)


	async def update_bunk_redis(
			self, bunk_id: int, bunk_status: BunkStatus,
			bunk_number: int, room_number: int,
			dispensary_id: int
	) -> None:
		bunk_model = BunkResponse(
			id=bunk_id,
			bunk_status=bunk_status,
			room_number=room_number,
			dispensary_id=dispensary_id,
			bunk_number=bunk_number
		)

		self.redis_client.set(bunk_id, json.dumps(jsonable_encoder(bunk_model)))



