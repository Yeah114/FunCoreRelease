from .init import LIB, toPyString
from .defines import Event
from typing import Tuple, Optional

LIB.EventPoll.restype = Event
def EventPoll() -> Tuple[Optional[str], Optional[str]]:
    """轮询事件队列"""
    event = LIB.EventPoll()
    return toPyString(event.type), toPyString(event.retriever)