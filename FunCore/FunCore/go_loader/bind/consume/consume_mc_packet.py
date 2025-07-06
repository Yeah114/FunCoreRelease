from .init import LIB, toPyInt, toPyString, toPyBytes
from .defines import ConsumeMCPacket_return
from typing import Tuple, Optional
import ctypes

LIB.ConsumeMCPacket.restype = ConsumeMCPacket_return
def ConsumeMCPacket() -> Tuple[Optional[bytes], int, Optional[str]]:
    """消费 MC 数据包"""
    result = LIB.ConsumeMCPacket()
    packet_bytes, length, convert_error = result.packet_bytes, toPyInt(result.length), toPyString(result.convert_error)
    
    if convert_error:
        return None, length, convert_error
    
    if not packet_bytes or length <= 0:
        return None, 0, "无效数据包"
    
    try:
        # 复制数据并释放原始内存
        packet_data_bytes = toPyBytes(ctypes.string_at(packet_bytes, length))
        return packet_data_bytes, length, None
    except Exception as e:
        return None, 0, f"数据复制错误: {str(e)}"
