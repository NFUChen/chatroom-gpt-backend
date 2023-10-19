
class PersonalRoomListService:
    
    def __init__(self, personal_room_list_dict: dict[int, list[str]]) -> None:
        self.personal_room_list_dict = personal_room_list_dict

    def add_peronal_room(self, user_id: int, room_id: str) -> None:
        if user_id not in self.personal_room_list_dict:
            self.personal_room_list_dict[user_id] = []
            self.personal_room_list_dict[user_id].append(room_id)
            return
        
        personal_rooms = self.personal_room_list_dict[user_id]
        if room_id in personal_rooms:
            return
        personal_rooms.append(room_id)
    def delete_personal_room(self, user_id: int, room_id: str) -> None:
        if user_id not in self.personal_room_list_dict:
            return
        
        personal_rooms = self.personal_room_list_dict[user_id]
        if room_id not in personal_rooms:
            return
        personal_rooms.remove(room_id)

    def get_personal_rooms(self, user_id: int) -> list[str]:
        if user_id not in self.personal_room_list_dict:
            return []
        return self.personal_room_list_dict[user_id]
    
    def is_personal_room_of_user(self, user_id: int, room_id: str) -> bool:
        if user_id not in self.personal_room_list_dict:
            return False
        return room_id in self.personal_room_list_dict[user_id]
    


    