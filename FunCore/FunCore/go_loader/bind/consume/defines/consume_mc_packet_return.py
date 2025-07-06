from ..init import CStructure, CBytes, GoInt, CString

# MC 数据包事件返回
class ConsumeMCPacket_return(CStructure):
    """MC 数据包返回结构"""
    _fields_ = [
        ("packet_bytes", CBytes),   # 数据包字节
        ('length', GoInt),          # 数据长度
        ("convert_error", CString)  # 转换错误
    ]
