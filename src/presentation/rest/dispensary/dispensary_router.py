from typing import Optional

from fastapi import APIRouter, status, Query, Depends

from src.domain.authorization.auth import get_token
from src.domain.dispensary.dispensary_service import DispensaryService
from src.domain.dispensary.schema import AllDispensaries, DispensaryPutModel,  DispensaryResponseForGet
from src.domain.dispensary.schema import DispensaryResponseForPut, DispensaryResponseForPost
from src.domain.dispensary.schema import DispensaryWithAvailableBunks

dispensary_router = APIRouter(prefix="/Dispensary", tags=["Dispensaries"])

dispensary_service = DispensaryService()

@dispensary_router.get("", response_model=AllDispensaries, status_code=status.HTTP_200_OK)
async def get_dispensaries(
		dispensary_id: Optional[int] = Query(None, description="The Id of the dispensary"),
		dispensary_name: Optional[str] = Query(None, description="The address of the dispensary"),
		address: Optional[str] = Query(None, description="The address of the dispensary")
) -> AllDispensaries:
	return await dispensary_service.get_dispensaries_service(dispensary_id, dispensary_name, address)


@dispensary_router.post("", response_model=DispensaryResponseForPost, status_code=status.HTTP_201_CREATED)
async def add_dispensary(
		dispensary_name: str = Query(..., description="The name of the dispensary"),
		address: str = Query(..., description="The address of the dispensary"),
		token: str = Depends(get_token)
) -> DispensaryResponseForPost:
	return await dispensary_service.add_dispensary_service(dispensary_name, address, token)


@dispensary_router.get("/{dispensary_id}", response_model=DispensaryResponseForGet, status_code=status.HTTP_200_OK)
async def get_dispensary_by_id(dispensary_id: int) -> DispensaryResponseForGet:
	return await dispensary_service.get_dispensary_by_id_service(dispensary_id)

@dispensary_router.get("/available_bunks/{dispensary_id}",
                       response_model=DispensaryWithAvailableBunks, status_code=status.HTTP_200_OK)
async def get_available_bunks(dispensary_id: int) -> DispensaryWithAvailableBunks:
	return await dispensary_service.get_available_bunks_in_dispensary(dispensary_id)


@dispensary_router.delete("/{dispensary_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dispensary(dispensary_id: int, token: str = Depends(get_token)) -> None:
	return await dispensary_service.delete_dispensary_by_id_service(dispensary_id, token)


@dispensary_router.put("/{dispensary_id}", response_model=DispensaryPutModel, status_code=status.HTTP_200_OK)
async def update_dispensary(
		dispensary_id: int, dispensary_name: str = Query(None, description="The name of the dispensary"),
		address: str = Query(None, description="The address of the dispensary"),
		token: str = Depends(get_token)
) -> DispensaryPutModel:
	return await dispensary_service.update_dispensary_service(dispensary_id, dispensary_name, address, token)


@dispensary_router.patch("/{dispensary_id}", response_model=DispensaryResponseForPut, status_code=status.HTTP_200_OK)
async def update_dispensary_status(dispensary_id: int, token: str = Depends(get_token)) -> DispensaryResponseForPut:
	return await dispensary_service.update_dispensary_status_service(dispensary_id, token)

