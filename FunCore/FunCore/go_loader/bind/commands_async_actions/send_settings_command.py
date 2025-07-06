from .init import LIB, CString, toCString

LIB.SendWOCommand.argtypes = [CString]
def SendSettingsCommand(cmd: str):
    """发送 WO 命令"""
    LIB.SendWOCommand(toCString(cmd))
