from ..init import CStructure, CBytes, GoInt, CString

class MarshalUQHolderData_return(CStructure):
    """UQHolder 数据返回结构"""
    _fields_ = [
        ("uqholder_bytes", CBytes),   # UQHolder 字节
        ('length', GoInt),          # 数据长度
        ("marshal_error", CString)  # 编码错误
    ]
