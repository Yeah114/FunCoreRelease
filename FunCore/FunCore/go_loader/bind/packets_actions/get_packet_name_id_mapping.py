from .init import LIB, CString, toPyString
from typing import Dict
import json

LIB.GetPacketNameIDMapping.restype = CString
def GetPacketNameIDMapping() -> Dict[str, int]:
    """获取数据包名称与 ID 的映射"""
    mapping_ptr = LIB.GetPacketNameIDMapping()
    if not mapping_ptr:
        return {}
    
    mapping_str = toPyString(mapping_ptr)
    return json.loads(mapping_str) if mapping_str else {}
