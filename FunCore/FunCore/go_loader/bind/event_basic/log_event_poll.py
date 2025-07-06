from .init import LIB, toPyString
from .defines import LogEvent
from typing import Tuple, Optional

LIB.LogEventPoll.restype = LogEvent
def LogEventPoll() -> Tuple[Optional[str], Optional[str]]:
    """轮询日志事件队列"""
    event = LIB.LogEventPoll()
    return toPyString(event.level), toPyString(event.message)
