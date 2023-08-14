from typing import Iterator
class MessageQueue:
    def __init__(self) -> None:
        self.queue: list[dict[str, int | str]] = []

    def push(self, message:dict[str, int | str]) -> None:
        self.queue.append(message)
    
    def next(self) -> Iterator[dict[str, int | str] | None]:
        if len(self.queue) == 0:
            yield
        else:
            message = self.queue.pop(0)
            yield message