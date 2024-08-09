from typing import Optional

from fastapi import Query, HTTPException, status, Depends

from src.domain.bunk.schema import BunkModel, BunkResponseForPut, BunkResponseForPost
from src.domain.bunk.schema import AllBunks, BunkResponseForGet, AvailableBunks
from src.domain.enums import BunkStatus
from src.configs.logger_setup import logger
from src.domain.bunk.functions import BunkFunctions
from src.infrastructure.database.postgres.create_db import dispensary, bunk
from src.domain.authorization.auth import get_token
from src.domain.authorization.dependencies import check_user_is_doctor


class BunkService(BunkFunctions):
	def __init__(self) -> None:
		super().__init__()


	async def get_bunks_service(
			self, bunk_status: Optional[BunkStatus] = None,
			room_number: Optional[int] = None,
			dispensary_id: Optional[int] = None
	) -> AllBunks:
		all_bunks = await self.get_bunks_function(bunk_status, room_number, dispensary_id)
		logger.info("Bunks sent from DB")

		return AllBunks(Bunks=all_bunks)


	async def add_bunk_service(
			self, dispensary_id: int = Query(..., description="The dispensary id of the bunk"),
			room_number: int = Query(..., description="The room number of the bunk"),
			bunk_number: int = Query(..., description="The number of the bunk"),
			token: str = Depends(get_token)
	) -> BunkResponseForPost:

		await check_user_is_doctor(dispensary_id, token)

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

		bunk_id = await bunk.insert_bunk(bunk_model)

		logger.info("Bunk added successfully")

		return BunkResponseForPost(BunkId=bunk_id)


	async def get_available_bunks_service(self) -> AvailableBunks:
		bunks_list = await self.get_available_bunks_function()
		logger.info("Bunks sent from DB")

		return AvailableBunks(Bunks=bunks_list)


	@staticmethod
	async def update_bunk_status_by_id_service(bunk_id: int, bunk_status: BunkStatus) -> BunkResponseForPut:
		bunk_by_id = await bunk.select_bunk_by_id(bunk_id)

		if bunk_by_id is None:
			logger.warning("Bunk not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bunk not found")

		await bunk.update_bunk_by_id(bunk_id, bunk_status)

		logger.info("Bunk updated successfully")

		return BunkResponseForPut(
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



