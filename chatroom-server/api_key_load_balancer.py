class ApiKeyLoadBalancer:
    def __init__(self, api_keys: list[str]) -> None:
        self.keys = api_keys
        self.idx = 0
    def get_key(self) -> str:
        if len(self.keys) == 0:
            raise ValueError("No API keys")

        current_key = self.keys[self.idx]
        self.idx += 1
        if self.idx > len(self.keys) - 1:
            self.idx = 0
        return current_key

