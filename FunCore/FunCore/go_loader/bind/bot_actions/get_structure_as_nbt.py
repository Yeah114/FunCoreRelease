from .init import LIB, GoInt32, toGoInt32, toPyInt, toPyString, toPyBytes
from .defines import GetStructureAsNBT_return
from typing import Tuple, Optional
import ctypes

LIB.GetStructureAsNBT.argtypes = [GoInt32, GoInt32, GoInt32, GoInt32, GoInt32, GoInt32]
LIB.GetStructureAsNBT.restype = GetStructureAsNBT_return
def GetStructureAsNBT(
    origin_x: int,
    origin_y: int,
    origin_z: int,
    size_x: int,
    size_y: int,
    size_z: int,
) -> Tuple[Optional[bytes], Optional[int], Optional[str]]:
    """
    获取一个区域的结构(NBT 形式)
    
    参数:
        origin_x: 起始点 X
        origin_y: 起始点 Y
        origin_z: 起始点 Z
        size_x: X 长度
        size_y: Y 长度
        size_z: Z 长度
        
    返回:
        (结构字节, 结构字节长度, 错误信息)
    """
    result = LIB.GetStructureAsNBT(
        toGoInt32(origin_x),
        toGoInt32(origin_y),
        toGoInt32(origin_z),
        toGoInt32(size_x),
        toGoInt32(size_y),
        toGoInt32(size_z),
    )
    structure_nbt_bytes, length, convert_error = result.structure_nbt_bytes, toPyInt(result.length), toPyString(result.convert_error)
    if convert_error:
        return None, length, convert_error
    
    if not structure_nbt_bytes or length <= 0:
        return None, 0, "无效结构 NBT"
    
    try:
        # 复制数据并释放原始内存
        structure_nbt_data_bytes = toPyBytes(ctypes.string_at(structure_nbt_bytes, length))
        return structure_nbt_data_bytes, length, None
    except Exception as e:
        return None, 0, f"数据复制错误: {str(e)}"
