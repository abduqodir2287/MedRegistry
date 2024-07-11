from fastapi import HTTPException, status

from src.configs.logger_setup import logger
from src.domain.dispensary.schema import DispensaryResponse, DispensaryResponseForPost
from src.infrastructure.database.postgres.create_db import dispensary
from src.domain.dispensary.schema import DispensaryModel


class DispensariesFunctions:

	def __init__(self):
		pass

	async def get_dispensaries_function(self) -> list:
		dispensaries_list = []
		for dispensaries in await dispensary.select_all_dispensaries():
			returned_dispensary = DispensaryResponse(
				id=dispensaries.id,
				dispensary_name=dispensaries.dispensary_name,
				address=dispensaries.address
			)
			dispensaries_list.append(returned_dispensary)
		return dispensaries_list


	async def add_id_function(self, id: int, dis_model: DispensaryModel) -> DispensaryResponseForPost:
		return DispensaryResponseForPost(
			result="Task Added",
			id=id,
			dispensary_name=dis_model.dispensary_name,
			address=dis_model.address
		)


	async def update_response_function(self, id: int, dis_model: DispensaryModel) -> DispensaryResponseForPost:
		return DispensaryResponseForPost(
			result="Task updated",
			id=id,
			dispensary_name=dis_model.dispensary_name,
			address=dis_model.address
		)



