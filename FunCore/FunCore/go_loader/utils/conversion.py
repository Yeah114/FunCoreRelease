from .alias import GoInt, GoInt32, CString, GoFloat32
import ctypes

# 类型转换辅助函数
def toGoInt(i: int) -> GoInt:
    """Python int -> Goint"""
    return GoInt(i)

def toGoInt32(i: int) -> GoInt32:
    """Python int -> Go int32"""
    return GoInt32(i)

def toCString(string: str) -> CString:
    """Python str -> C string"""
    return ctypes.c_char_p(string.encode("utf-8"))

def toPyInt(i: GoInt) -> int:
    """Go int -> Python int"""
    return int(i)

def toPyBool(b) -> bool:
    """Go bool -> Python bool"""
    return bool(b)

def toPyString(cstring: CString) -> str:
    """C string -> Python str"""
    if cstring is None:
        return ""
    return bytes(cstring).decode("utf-8") if cstring else ""

def toPyBytes(cstring: CString | bytes) -> bytes:
    """C string -> Python bytes"""
    if cstring is None:
        return b""
    return bytes(cstring)

def toGoFloat32(f: float | int) -> GoFloat32:
    """Python float -> GoFloat32"""
    return GoFloat32(float(f))
