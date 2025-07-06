from .init import LIB, CString, GoBool, toPyBool, toCString

LIB.SendTotalWOCommand.argtypes = [CString]
LIB.SendTotalWOCommand.restypes = GoBool
def SendTotalSettingsCommand(cmds: str) -> bool:
    """发送大量 WO 命令"""
    return toPyBool(LIB.SendTotalWOCommand(toCString(cmds)))
