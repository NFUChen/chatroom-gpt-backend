from room_database_manager import room_db_manager
from room import Room
class RoomManager:
    def __init__(self, rooms: list[Room] = []) -> None:
        self.rooms_dict = {
            room.room_id: room for room in rooms
        }
    
    def get_room_by_id(self, room_id: str) -> Room:
        if room_id not in self.rooms_dict:
            raise ValueError(f"Room {room_id} not found")

        return self.rooms_dict[room_id]
    
    def add_room(self, room: Room) -> None:

        # add room to db via publisher
        room_db_manager.add_room(room)
        self.rooms_dict[room.room_id] = room
    
    def pop_room(self, room_id: str) -> Room:
        if room_id not in self.rooms_dict:
            raise ValueError(f"Room {room_id} not found")
        # delete room to db via publisher
        target_room = self.rooms_dict[room_id]
        room_db_manager.delete_room(target_room)

        return self.rooms_dict.pop(room_id)
    
    def get_all_rooms_info(self) -> list[dict[str, str]]:
        return [room.to_dict() for room in self.rooms_dict.values()]
