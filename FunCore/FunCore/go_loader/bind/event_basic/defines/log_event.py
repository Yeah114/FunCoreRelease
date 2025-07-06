from ..init import CStructure, CString

# 日志事件
class LogEvent(CStructure):
    """事件数据结构"""
    _fields_ = [
        ("level", CString),      # 日志等级
        ("message", CString)  # 日志信息
    ]
