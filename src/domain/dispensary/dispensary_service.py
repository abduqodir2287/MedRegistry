from fastapi import Query, HTTPException, status

from src.domain.dispensary.schema import DispensaryResponseForPost, AllDispensaries
from src.domain.dispensary.schema import DispensaryModel, DispensaryResponse
from src.configs.logger_setup import logger
from src.domain.dispensary.functions import DispensariesFunctions
from src.infrastructure.database.postgres.create_db import dispensary


class DispensaryService(DispensariesFunctions):
	def __init__(self) -> None:
		super().__init__()


	async def get_dispensaries_service(self) -> AllDispensaries:
		all_dispensaries = await self.get_dispensaries_function()
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



	async def delete_dispensary_by_id_service(self, dispensary_id: int) -> None:
		result = await dispensary.delete_dispensary_by_id(dispensary_id)

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
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

		update_model = DispensaryModel(
			dispensary_name=dispensary_name if dispensary_name is not None else dispensary_by_id.dispensary_name,
			address=address if address is not None else dispensary_by_id.address
		)

		await dispensary.update_dispensary_by_id(id, update_model)
		result = await self.update_response_function(id, update_model)
		logger.info("Dispensary updated successfully")

		return result

	async def get_dispensary_by_id_service(self, id: int) -> DispensaryResponse:
		dispensary_by_id = await dispensary.select_dispensary_by_id(id)

		if dispensary_by_id is None:
			logger.warning("Dispensary not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispensary not found")

		logger.info("Dispensary sent successfully")
		return DispensaryResponse(
			id=id,
			dispensary_name=dispensary_by_id.dispensary_name,
			address=dispensary_by_id.address
		)


