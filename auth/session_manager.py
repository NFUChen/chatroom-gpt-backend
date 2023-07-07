from session_store import session_store
class SessionResult:
    def __init__(self) -> None:
        pass

class SessionManager:
    def __init__(self, sid: str) -> None:
        self.sid = sid
    
    def is_valid_sid(self) -> bool:
        return session_store.is_valid_sid(self.sid)