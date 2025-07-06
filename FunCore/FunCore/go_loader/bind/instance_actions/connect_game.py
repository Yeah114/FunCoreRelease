from .init import LIB, CString, GoInt32, toCString, toGoInt32, toPyString
from typing import Optional

LIB.ConnectGame.restype = CString
LIB.ConnectGame.argtypes = [CString, CString, CString, CString, GoInt32, GoInt32, GoInt32]
def ConnectGame(
    auth_server: str,   # 验证服务器地址
    auth_token: str,    # 验证服务器 token
    server_code: str,   # 租赁服号码
    server_passcode: str, # 租赁服密码 
    console_center_x: int, # 控制台中心 X 坐标
    console_center_y: int, # 控制台中心 Y 坐标
    console_center_z: int, # 控制台中心 Z 坐标
) -> Optional[str]:
    """
    连接到游戏服务器
    
    返回:
        错误信息(成功时为 None)
    """
    err_ptr = LIB.ConnectGame(
        toCString(auth_server),
        toCString(auth_token),
        toCString(server_code),
        toCString(server_passcode),
        toGoInt32(console_center_x),
        toGoInt32(console_center_y),
        toGoInt32(console_center_z),
    )
    
    if err_ptr:
        err_msg = toPyString(err_ptr)
        return err_msg
    return None
