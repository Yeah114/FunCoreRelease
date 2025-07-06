from ..init import CStructure, CBytes, GoInt, CString

class GetStructureAsNBT_return(CStructure):
    """结构 NBT 返回结构"""
    _fields_ = [
        ("structure_nbt_bytes", CBytes),   # 结构 NBT 字节
        ('length', GoInt),          # 数据长度
        ("convert_error", CString)  # 转换错误
    ]
