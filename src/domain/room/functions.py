from src.infrastructure.database.postgres.create_db import room
from src.domain.room.schema import RoomResponse, RoomModel, RoomResponseForPost


class RoomsFunctions:

	def __init__(self):
		pass

	async def get_rooms_function(self) -> list:
		rooms_list = []
		for rooms in await room.select_all_rooms():
			returned_room = RoomResponse(
				id=rooms.id,
				room_status=rooms.room_status,
				room_number=rooms.room_number,
				dispensary_id=rooms.dispensary_id
			)
			rooms_list.append(returned_room)

		return rooms_list

	async def add_id_function(self, id: int, room_model: RoomModel) -> RoomResponseForPost:
		return RoomResponseForPost(
			id=id,
			room_number=room_model.room_number,
			dispensary_id=room_model.dispensary_id
		)


