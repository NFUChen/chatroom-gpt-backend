from chat_room_database_manager import chat_room_db_manager
from room import Room
class RoomManager:
    def __init__(self, rooms: list[Room] = []) -> None:
        self.rooms_dict = {
            room.room_id: room for room in rooms
        }
        self.user_location_dict:dict[str, str] = {}
    
    def user_join_room(self,full_user_id: str, room_id: str ) -> Room:

        if full_user_id in self.user_location_dict:
            raise ValueError(f"User [{full_user_id}] aleady in {self.user_location_dict[full_user_id]}")
        if room_id not in self.rooms_dict:
            raise ValueError(f"Room {room_id} not found")
        
    

        self.user_location_dict[full_user_id] = room_id
        
        room = self.rooms_dict[room_id]
        room.user_join_room(full_user_id)

        return room

    def user_leave_room(self, full_user_id: str) -> Room:
        if full_user_id not in self.user_location_dict:
            raise ValueError(f"User [{full_user_id}] have not joined any rooms")
        
        room_id = self.user_location_dict.pop(full_user_id)
        room = self.rooms_dict[room_id]
        room.user_leave_room(full_user_id)

        return room
    
    def get_user_location(self, full_user_id: str, raise_if_not_found: bool = True) -> str | None:
        if raise_if_not_found and (full_user_id not in self.user_location_dict):
            raise ValueError(f"User [{full_user_id}] have not joined any rooms")
        
        return self.user_location_dict.get(full_user_id)
    
    def get_room_by_id(self, room_id: str) -> Room:
        if room_id not in self.rooms_dict:
            raise ValueError(f"Room {room_id} not found")

        return self.rooms_dict[room_id]
    
    def add_room(self, room: Room) -> None:

        # add room to db via publisher
        chat_room_db_manager.add_room(room)
        self.rooms_dict[room.room_id] = room
    
    def pop_room(self, room_id: str) -> Room:
        if room_id not in self.rooms_dict:
            raise ValueError(f"Room {room_id} not found")
        # delete room to db via publisher
        target_room = self.rooms_dict[room_id]
        chat_room_db_manager.delete_room(target_room)
        
        # clear who have joined this deleted room
        self.user_location_dict = {
            user_id: room_id 
            for user_id, room_id in self.user_location_dict.items() 
            if room_id != room_id
        }
        
        return self.rooms_dict.pop(room_id)
    
    def get_all_rooms_info(self, filter_room_name: str) -> list[dict[str, str]]:
        return [
            room.to_dict() 
            for room in self.rooms_dict.values() 
            if filter_room_name in room.room_name
        ]
