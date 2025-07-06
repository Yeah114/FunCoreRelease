from .init import LIB, CString, toPyString
from typing import Optional

LIB.GetBotXUID.restype = CString
def GetBotXUID() -> Optional[str]:
    """获取机器人 XUID"""
    return toPyString(LIB.GetBotXUID())
