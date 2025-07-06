from .init import LIB, CString, toPyString
from typing import Optional

LIB.ConsumeCommandResponseCB.restype = CString
def ConsumeCommandResponseCB() -> Optional[str]:
    """消费命令响应回调"""
    result = LIB.ConsumeCommandResponseCB()
    return toPyString(result) if result else None
