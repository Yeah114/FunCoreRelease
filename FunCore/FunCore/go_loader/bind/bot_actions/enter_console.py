from .init import LIB, CString, toPyString
from typing import Optional

LIB.EnterConsole.restype = CString
def EnterConsole() -> Optional[str]:
    """进入控制台"""
    error = LIB.EnterConsole()
    if error:
        return toPyString(error)
