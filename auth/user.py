from dataclasses import dataclass
@dataclass
class User:
    email: str
    user_name: str
    hashed_password: str = None

    def to_dict(self) -> dict[str, str]:
        return {
            "email": self.email,
            "user_name": self.user_name,
        } 