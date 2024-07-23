from fastapi import Query, HTTPException, status

from src.domain.bunk.schema import BunkStatus, BunkModel, BunkResponseForPost, AllBunks, BunkResponseForGet
from src.configs.logger_setup import logger
from src.domain.bunk.functions import BunkFunctions
from src.infrastructure.database.postgres.create_db import dispensary, bunk


class BunkService(BunkFunctions):
	def __init__(self) -> None:
		super().__init__()


	async def get_bunks_service(self) -> AllBunks:
		all_bunks = await self.get_bunks_function()
		logger.info("Bunks sent from Redis")

		return AllBunks(Bunks=all_bunks)


	async def add_bunk_service(
			self, dispensary_id: int = Query(..., description="The dispensary id of the bunk"),
			room_number: int = Query(..., description="The room number of the bunk"),
			bunk_number: int = Query(..., description="The number of the bunk")
	) -> BunkResponseForPost:

		bunk_model = BunkModel(
			room_number=room_number,
			dispensary_id=dispensary_id,
			bunk_number=bunk_number
		)

		exist_dispensary = await dispensary.dispensary_exists(dispensary_id)
		if not exist_dispensary:
			logger.warning("Dispensary not found")
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="There is no Dispensary with this id."
			)

		if not await dispensary.select_dispensary_status(dispensary_id):
			logger.warning("Dispensary status is False")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This dispensary is not active right now")

		await self.check_room(room_number, dispensary_id)
		await self.check_bunk(dispensary_id, room_number, bunk_number)

		insert_response = await bunk.insert_bunk(bunk_model)
		# await self.add_bunk_redis(insert_response, bunk_model)

		result = await self.add_id_function(insert_response, bunk_model)
		logger.info("Bunk added successfully")

		return result


	async def delete_bunk_by_id_service(self, bunk_id: int) -> None:
		result = await bunk.delete_bunk_by_id(bunk_id)

		if result is None:
			logger.warning("Bunk not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bunk not found")

		self.redis_client.delete(bunk_id)
		logger.info("Bunk deleted successfully")


	async def update_bunk_status_by_id_service(self, bunk_id: int, bunk_status: BunkStatus) -> BunkResponseForPost:
		bunk_by_id = await bunk.select_bunk_by_id(bunk_id)

		if bunk_by_id is None:
			logger.warning("Bunk not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bunk not found")

		await bunk.update_bunk_by_id(bunk_id, bunk_status)
		await self.update_bunk_redis(
			bunk_id, bunk_status, bunk_by_id.bunk_number,
			bunk_by_id.room_number, bunk_by_id.dispensary_id
		)

		return BunkResponseForPost(
			result="Bunk Updated",
			id=bunk_id,
			bunk_status=bunk_status,
			dispensary_id=bunk_by_id.dispensary_id,
			room_number=bunk_by_id.room_number,
			bunk_number=bunk_by_id.bunk_number
		)


	async def get_bunk_by_number_service(
			self, dispensary_id: int, room_number: int,
			bunk_number: int
	) -> BunkResponseForGet:
		bunk_by_number = await self.get_bunk_by_number_function(dispensary_id, room_number, bunk_number)

		return bunk_by_number



