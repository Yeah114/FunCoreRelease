from .init import LIB, CString, toPyString
from typing import Optional

LIB.GetBotIdentity.restype = CString
def GetBotIdentity() -> Optional[str]:
    """获取机器人 UUID"""
    return toPyString(LIB.GetBotIdentity())
