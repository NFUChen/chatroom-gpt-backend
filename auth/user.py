from dataclasses import dataclass
@dataclass
class User:
    user_id: int
    user_email: str
    user_name: str
    is_deleted: bool
    password: str = None

    def to_dict(self) -> dict[str, str]:
        return self.__dict__