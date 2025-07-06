from .init import LIB, CString, toCString

LIB.SendPlayerCommandOmitResponse.argtypes = [CString]
def SendPlayerCommandOmitResponse(cmd: str):
    """发送 Player 命令(忽略响应)"""
    LIB.SendPlayerCommandOmitResponse(toCString(cmd))
