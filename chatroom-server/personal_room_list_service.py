
class PersonalRoomListService:
    '''
    This service is responsible for doing CRUD operation for personal room list (what room they had joined).
    user_id_with_room_list_dict:
    {
        "wichen": ["room_x", "room_y"],
        "rili": ["room_x", "room_y"]
    }
    '''
    def __init__(self, user_id_with_room_list_dict: dict[str, list[str]]) -> None:
        self.user_id_with_room_list_dict = user_id_with_room_list_dict

    def __vaidate_valid_user_id(self, user_id: str) -> None:
        if user_id not in self.user_id_with_room_list_dict:
            raise ValueError(f"User ID: {user_id} not in {self.user_id_with_room_list_dict.keys()}")

    def get_room_list_by_user_id(self, user_id: str) -> list[str]:
        return self.user_id_with_room_list_dict.get(user_id, [])
    
    def user_add_room(self, user_id: str, room_id: str) -> None:
        if user_id not in self.user_id_with_room_list_dict:
            self.user_id_with_room_list_dict[user_id] = [room_id]
            return
        room_list = self.user_id_with_room_list_dict[user_id]
        if room_id in room_list:
            print(f"Room ID: {room_id} is already in {room_list}")
            return
        room_list.append(room_id)
        # add to SQL


    def user_delete_room(self, user_id: str, room_id: str) -> None:
        self.__vaidate_valid_user_id(user_id)
        room_list = self.user_id_with_room_list_dict[user_id]
        if room_id not in room_list:
            print(f"Room ID: {room_id} is not in {room_list}")
            return
        room_list.remove(room_id)
        # remove from SQL