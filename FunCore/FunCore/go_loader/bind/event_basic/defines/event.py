from ..init import CStructure, CString

# 游戏事件
class Event(CStructure):
    """事件数据结构"""
    _fields_ = [
        ("type", CString),      # 事件类型
        ("retriever", CString)  # 检索器ID
    ]
