from .init import LIB, CString, toPyString, toGoFloat32
from typing import Optional

LIB.MoveToPosition.restype = CString
def MoveToPosition(
        x: float | int,
        y: float | int,
        z: float | int,
        pitch: float | int,
        yaw: float | int,
        head_yaw: float | int,
) -> Optional[str]:
    """移动到一个坐标"""
    error = LIB.MoveToPosition(
        toGoFloat32(x),
        toGoFloat32(y),
        toGoFloat32(z),
        toGoFloat32(pitch),
        toGoFloat32(yaw),
        toGoFloat32(head_yaw)
    )
    if error:
        return toPyString(error)
