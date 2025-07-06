from .init import LIB, GoBool, toPyBool

LIB.GameAvailable.restype = GoBool
def GameAvailable() -> bool:
    """检查实例是否可用"""
    return toPyBool(LIB.GameAvailable())
