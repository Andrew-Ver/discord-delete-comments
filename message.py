from dataclasses import dataclass


@dataclass
class Message():
    channel_id: int
    comment_id: int
    content: str 
    timestamp: int


if __name__ == 'main':
    ...