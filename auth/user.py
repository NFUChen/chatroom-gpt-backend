from dataclasses import dataclass
@dataclass
class User:
    user_id: int
    user_email: str
    user_name: str
    password: str = None

    def to_dict(self) -> dict[str, str]:
        return {
            "user_id": self.user_id,
            "user_email": self.user_email,
            "user_name": self.user_name,
        } 