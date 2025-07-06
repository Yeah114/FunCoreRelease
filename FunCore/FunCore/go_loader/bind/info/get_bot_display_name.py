from .init import LIB, CString, toPyString
from typing import Optional

LIB.GetBotDisplayName.restype = CString
def GetBotDisplayName() -> Optional[str]:
    """获取机器人名称"""
    return toPyString(LIB.GetBotDisplayName())
