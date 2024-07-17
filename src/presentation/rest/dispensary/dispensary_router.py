from fastapi import APIRouter, status, Query

from src.domain.dispensary.dispensary_service import DispensaryService
from src.domain.dispensary.schema import AllDispensaries, DispensaryResponseForPost, DispensaryResponse


dispensary_router = APIRouter(prefix="/Dispensary", tags=["Dispensaries"])

dispensary_service = DispensaryService()

@dispensary_router.get("", response_model=AllDispensaries, status_code=status.HTTP_200_OK)
async def get_dispensaries() -> AllDispensaries:
	return await dispensary_service.get_dispensaries_service()


@dispensary_router.post("", response_model=DispensaryResponseForPost, status_code=status.HTTP_200_OK)
async def add_dispensary(
		dispensary_name: str = Query(..., description="The name of the dispensary"),
		address: str = Query(..., description="The address of the dispensary")
) -> DispensaryResponseForPost:
	return await dispensary_service.add_dispensary_service(dispensary_name, address)


@dispensary_router.get("/dispensary_id", response_model=DispensaryResponse, status_code=status.HTTP_200_OK)
async def get_dispensaries(dispensary_id: int) -> DispensaryResponse:
	return await dispensary_service.get_dispensary_by_id_service(dispensary_id)


@dispensary_router.delete("/dispensary_id", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dispensary(dispensary_id: int) -> None:
	return await dispensary_service.delete_dispensary_by_id_service(dispensary_id)


@dispensary_router.put("/dispensary_id", response_model=DispensaryResponseForPost, status_code=status.HTTP_200_OK)
async def update_dispensary(
		id: int, dispensary_name: str = Query(None, description="The name of the dispensary"),
		address: str = Query(None, description="The address of the dispensary")
) -> DispensaryResponseForPost:
	return await dispensary_service.update_dispensary_service(id, dispensary_name, address)

