from fastapi import APIRouter, status, Query

from src.domain.bunk.bunk_service import BunkService
from src.domain.bunk.schema import AllBunks, BunkResponseForPost, BunkResponseForGet

bunk_router = APIRouter(prefix="/Bunk", tags=["Bunks"])

bunk_service = BunkService()


@bunk_router.get("", response_model=AllBunks, status_code=status.HTTP_200_OK)
async def get_bunks() -> AllBunks:
	return await bunk_service.get_bunks_service()


@bunk_router.post("", response_model=BunkResponseForPost, status_code=status.HTTP_200_OK)
async def add_bunk(
		dispensary_id: int = Query(..., description="The dispensary id of the bunk"),
		room_number: int = Query(..., description="The room number of the bunk"),
		bunk_number: int = Query(..., description="The number of the bunk")
) -> BunkResponseForPost:
	return await bunk_service.add_bunk_service(dispensary_id, room_number, bunk_number)


@bunk_router.get("/bunk_number/dispensary_id/room_number",
                 response_model=BunkResponseForGet, status_code=status.HTTP_200_OK)
async def get_bunk_by_number(
		dispensary_id: int = Query(..., description="The dispensary id of the bunk"),
		room_number: int = Query(..., description="The room number of the bunk"),
		bunk_number: int = Query(..., description="The number of the bunk")
) -> BunkResponseForGet:
	return await bunk_service.get_bunk_by_number_service(dispensary_id, room_number, bunk_number)


@bunk_router.delete("/{bunk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bunk_by_id(bunk_id: int) -> None:
	await bunk_service.delete_bunk_by_id_service(bunk_id)


# @bunk_router.patch("/bunk_id", response_model=BunkResponseForPost, status_code=status.HTTP_200_OK)
# async def update_bunk_status_by_id(
# 		bunk_id: int,
# 		bunk_status: BunkStatus = Query(..., description="The status of the Bunk")
# ):
# 	return await bunk_service.update_bunk_status_by_id_service(bunk_id, bunk_status)

