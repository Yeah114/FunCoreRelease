from .init import LIB, toPyInt, toPyString, toPyBytes
from .defines import MarshalUQHolderData_return
from typing import Tuple, Optional
import ctypes

LIB.GetUQHolderData.restype = MarshalUQHolderData_return
def GetUQHolderData() -> Tuple[Optional[bytes], int, Optional[str]]:
    """获取 UQHolder 数据"""
    result = LIB.GetUQHolderData()
    uqholder_bytes, length, marshal_error = result.uqholder_bytes, toPyInt(result.length), toPyString(result.marshal_error)
    if marshal_error:
        return None, length, marshal_error
    
    try:
        # 复制数据并释放原始内存
        uqholder_data_bytes = toPyBytes(ctypes.string_at(uqholder_bytes, length))
        return uqholder_data_bytes, length, None
    except Exception as e:
        return None, 0, f"数据复制错误: {str(e)}"
