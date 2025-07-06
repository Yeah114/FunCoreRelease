from .init import LIB, CString, GoInt, toCString, toGoInt, toPyString, toPyBool, toPyInt
from .defines import PlaceNBTBlockInConsole_return
from typing import Tuple, Optional

LIB.PlaceNBTBlockInConsole.argtypes = [CString, CString, CString, GoInt]
LIB.PlaceNBTBlockInConsole.restype = PlaceNBTBlockInConsole_return
def PlaceNBTBlockInConsole(
    blockName: str,
    blockStatesString: str,
    blockNBTCBytes: bytes
) -> Tuple[bool, str, Tuple[int, int, int], Optional[str]]:
    """
    在控制台放置 NBT 方块
    
    参数:
        blockName: 方块名字
        blockStatesString: 方块状态字符串
        blockNBTCBytes: 方块 NBT 字节
        
    返回:
        (是否可快速放置, 唯一 ID, (x 偏移, y 偏移, z 偏移), 错误信息)
    """
    result = LIB.PlaceNBTBlockInConsole(
        toCString(blockName),
        toCString(blockStatesString),
        CString(blockNBTCBytes),
        toGoInt(len(blockNBTCBytes))
    )
    
    unique_id = toPyString(result.unique_id)
    error = toPyString(result.error)
    
    return (
        toPyBool(result.can_fast),
        unique_id,
        (toPyInt(result.offset_x), toPyInt(result.offset_y), toPyInt(result.offset_z)),
        error
    )
