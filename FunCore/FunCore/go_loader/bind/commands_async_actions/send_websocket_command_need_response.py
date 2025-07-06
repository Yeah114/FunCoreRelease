from .init import LIB, CString, toCString

LIB.SendWebSocketCommandNeedResponse.argtypes = [CString, CString]
def SendWebSocketCommandNeedResponse(cmd: str, retriever: str):
    """发送 WebSocket 命令(需要响应)"""
    LIB.SendWebSocketCommandNeedResponse(toCString(cmd), toCString(retriever))
