from .init import LIB, GoInt, CString, toGoInt, toCString
from typing import Optional

LIB.SendGamePacket.argtypes = [GoInt, CString]
LIB.SendGamePacket.restype = CString
def SendGamePacket(packetID: int, jsonStr: str) -> Optional[str]:
    """
    发送游戏数据包
    
    参数:
        packetID: 数据包 ID
        jsonStr: JSON 格式的数据包内容
        
    返回:
        error: 错误信息
    """
    err_ptr = LIB.SendGamePacket(toGoInt(packetID), toCString(jsonStr))
    if err_ptr:
        err_msg = toPyString(err_ptr)
        return err_msg
    return None
