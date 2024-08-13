from typing import Optional
from fastapi import Query, HTTPException, status, Depends

from src.domain.dispensary.schema import DispensaryPutModel, AllDispensaries, DispensaryResponseForGet
from src.domain.dispensary.schema import DispensaryResponseForPut, DispensaryResponseForPost
from src.domain.dispensary.schema import DispensaryModel, DispensaryWithAvailableBunks
from src.configs.logger_setup import logger
from src.domain.dispensary.functions import DispensariesFunctions
from src.domain.authorization.auth import get_token
from src.domain.authorization.dependencies import check_user_is_superadmin
from src.infrastructure.database.postgres.create_db import dispensary


class DispensaryService(DispensariesFunctions):
	def __init__(self) -> None:
		super().__init__()


	async def get_dispensaries_service(
			self, dispensary_id: Optional[int] = None,
			dispensary_name: Optional[str] = None,
			address: Optional[str] = None
	) -> AllDispensaries:
		all_dispensaries = await self.get_all_dispensaries(dispensary_id, dispensary_name, address)
		logger.info("Dispensaries sent from DB")

		return AllDispensaries(Dispensaries=all_dispensaries)


	@staticmethod
	async def add_dispensary_service(
			dispensary_name: str = Query(..., description="The name of the dispensary"),
			address: str = Query(..., description="The address of the dispensary"),
			token: str = Depends(get_token)
	) -> DispensaryResponseForPost:

		await check_user_is_superadmin(token)

		dispensary_model = DispensaryModel(
			dispensary_name=dispensary_name,
			address=address
		)

		dispensary_id = await dispensary.insert_dispensary(dispensary_model)

		logger.info("Dispensary added successfully")
		return DispensaryResponseForPost(DispensaryID=dispensary_id)


	@staticmethod
	async def delete_dispensary_by_id_service(dispensary_id: int, token: str = Depends(get_token)) -> None:
		await check_user_is_superadmin(token)

		result = await dispensary.update_dispensary_status(dispensary_id, False)

		if result is None:
			logger.warning("Dispensary not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispensary not found")

		logger.info("Now the status of the dispensary is False")


	async def get_available_bunks_in_dispensary(self, dispensary_id: int) -> DispensaryWithAvailableBunks:
		dispensary_by_id = await dispensary.select_dispensary_by_id(dispensary_id)
		bunks_list = await self.get_bunk_by_dispensary_id(dispensary_id)

		if dispensary_by_id is None:
			logger.warning("Dispensary with this id not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispensary with this id not found")

		if not dispensary_by_id.active:
			logger.info("Dispensary with this id is not active")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This dispensary is not active right now")

		if not bunks_list:
			logger.warning("No free bunks available in this dispensary")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
			                    detail="No free bunks available in this dispensary")

		logger.info("Available bunks sent from DB")

		return DispensaryWithAvailableBunks(
			id=dispensary_by_id.id,
			dispensary_name=dispensary_by_id.dispensary_name,
			address=dispensary_by_id.address,
			active=dispensary_by_id.active,
			free_bunks=bunks_list
		)


	async def update_dispensary_service(
			self, id: int, dispensary_name: str = Query(None, description="The name of the dispensary"),
			address: str = Query(None, description="The address of the dispensary"),
			token: str = Depends(get_token)
	) -> DispensaryPutModel:
		await check_user_is_superadmin(token)

		dispensary_by_id = await dispensary.select_dispensary_by_id(id)

		if dispensary_by_id is None:
			logger.warning("Dispensary not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispensary not found")

		if dispensary_name is None and address is None:
			logger.warning("User did not changed anything")
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You haven't changed anything")

		update_model = DispensaryModel(
			dispensary_name=dispensary_name if dispensary_name is not None else dispensary_by_id.dispensary_name,
			address=address if address is not None else dispensary_by_id.address
		)

		await dispensary.update_dispensary_by_id(id, update_model)

		result = await self.update_response_function(id, update_model)

		logger.info("Dispensary updated successfully")

		return result

	async def get_dispensary_by_id_service(self, id: int) -> DispensaryResponseForGet:
		dispensary_by_id = await self.get_dispensary_by_id_function(id)

		return dispensary_by_id


	@staticmethod
	async def update_dispensary_status_service(
			dispensary_id: int, token: str = Depends(get_token)) -> DispensaryResponseForPut:
		await check_user_is_superadmin(token)

		dispensary_by_id = await dispensary.select_dispensary_by_id(dispensary_id)

		if dispensary_by_id is None:
			logger.warning("Dispensary not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispensary not found")

		if dispensary_by_id.active:
			logger.warning("Dispensary already active")
			raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Dispensary already active")

		update = await dispensary.update_dispensary_status(dispensary_id, True)

		logger.info("The dispensary is active again")

		if update:
			return DispensaryResponseForPut(
				result="The dispensary is active again",
				id=dispensary_by_id.id,
				dispensary_name=dispensary_by_id.dispensary_name,
				address=dispensary_by_id.address,
				active=True
			)


