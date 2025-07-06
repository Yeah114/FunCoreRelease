from ..init import CStructure, GoBool, CString, GoInt32

class PlaceNBTBlockInConsole_return(CStructure):
    """放置NBT方块返回结构"""
    _fields_ = [
        ("can_fast", GoBool),   # 是否可以快速放置
        ("unique_id", CString), # uniqueID
        ("offset_x", GoInt32),  # 方块在控制台中的 X 坐标
        ("offset_y", GoInt32),  # 方块在控制台中的 Y 坐标
        ("offset_z", GoInt32),  # 方块在控制台中的 Z 坐标
        ("error", CString)      # 错误信息
    ]
