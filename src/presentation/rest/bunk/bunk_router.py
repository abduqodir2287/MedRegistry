from fastapi import APIRouter, status, Depends

from src.domain.bunk.bunk_service import BunkService
from src.domain.bunk.schema import AllBunks, BunkResponseForGet, AvailableBunks, BunkResponseForPost
from src.domain.authorization.auth import get_token

bunk_router = APIRouter(prefix="/Bunk", tags=["Bunks"])

bunk_service = BunkService()


@bunk_router.get("", response_model=AllBunks, status_code=status.HTTP_200_OK)
async def get_bunks() -> AllBunks:
	return await bunk_service.get_bunks_service()


@bunk_router.post("", response_model=BunkResponseForPost, status_code=status.HTTP_201_CREATED)
async def add_bunk(
		dispensary_id: int, room_number: int, bunk_number: int, token: str = Depends(get_token)) -> BunkResponseForPost:
	return await bunk_service.add_bunk_service(dispensary_id, room_number, bunk_number, token)


@bunk_router.get("/{bunk_number}/{dispensary_id}/{room_number}",
                 response_model=BunkResponseForGet, status_code=status.HTTP_200_OK)
async def get_bunk_by_number(dispensary_id: int, room_number: int, bunk_number: int) -> BunkResponseForGet:
	return await bunk_service.get_bunk_by_number_service(dispensary_id, room_number, bunk_number)


@bunk_router.get("/available_bunks", response_model=AvailableBunks, status_code=status.HTTP_200_OK)
async def get_available_bunks() -> AvailableBunks:
	return await bunk_service.get_available_bunks_service()

