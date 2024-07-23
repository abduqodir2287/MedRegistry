from fastapi import Query, HTTPException, status

from src.domain.dispensary.schema import DispensaryResponseForPost, AllDispensaries, DispensaryResponseForGet, \
	DispensaryResponseForPut
from src.domain.dispensary.schema import DispensaryModel
from src.configs.logger_setup import logger
from src.domain.dispensary.functions import DispensariesFunctions
from src.infrastructure.database.postgres.create_db import dispensary


class DispensaryService(DispensariesFunctions):
	def __init__(self) -> None:
		super().__init__()


	async def get_dispensaries_service(self) -> AllDispensaries:
		all_dispensaries = await self.get_all_dispensaries()
		logger.info("Dispensaries sent from DB")

		return AllDispensaries(Dispensaries=all_dispensaries)

	async def add_dispensary_service(
			self, dispensary_name: str = Query(..., description="The name of the dispensary"),
			address: str = Query(..., description="The address of the dispensary")
	) -> DispensaryResponseForPost:

		dispensary_model = DispensaryModel(
			dispensary_name=dispensary_name,
			address=address
		)

		insert_response = await dispensary.insert_dispensary(dispensary_model)

		result = await self.add_id_function(insert_response, dispensary_model)

		logger.info("Task added successfully")
		return result


	@staticmethod
	async def delete_dispensary_by_id_service(dispensary_id: int) -> None:
		result = await dispensary.update_dispensary_status(dispensary_id, False)

		if result is None:
			logger.warning("Dispensary not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispensary not found")

		logger.info("Dispensary deleted successfully")



	async def update_dispensary_service(
			self, id: int, dispensary_name: str = Query(None, description="The name of the dispensary"),
			address: str = Query(None, description="The address of the dispensary")
	) -> DispensaryResponseForPost:
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


	async def update_dispensary_status_service(self, dispensary_id: int) -> DispensaryResponseForPut:
		dispensary_by_id = await dispensary.select_dispensary_by_id(dispensary_id)

		if dispensary_by_id is None:
			logger.warning("Dispensary not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispensary not found")

		if dispensary_by_id.active:
			logger.warning("Dispensary already active")
			raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Dispensary already active")

		update = await dispensary.update_dispensary_status(dispensary_id, True)

		if update:
			return DispensaryResponseForPut(
				result="The dispensary is active again",
				id=dispensary_by_id.id,
				dispensary_name=dispensary_by_id.dispensary_name,
				address=dispensary_by_id.address,
				active=True
			)


