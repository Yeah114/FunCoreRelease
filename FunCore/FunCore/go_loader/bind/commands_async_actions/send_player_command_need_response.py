from .init import LIB, CString, toCString

LIB.SendPlayerCommandNeedResponse.argtypes = [CString, CString]
def SendPlayerCommandNeedResponse(cmd: str, retriever: str):
    """发送 Player 命令(需要响应)"""
    LIB.SendPlayerCommandNeedResponse(toCString(cmd), toCString(retriever))
