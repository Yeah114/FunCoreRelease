from .init import LIB, CString, toCString

LIB.SendWebSocketCommandOmitResponse.argtypes = [CString]
def SendWebSocketCommandOmitResponse(cmd: str):
    """发送 WebSocket 命令(忽略响应)"""
    LIB.SendWebSocketCommandOmitResponse(toCString(cmd))
