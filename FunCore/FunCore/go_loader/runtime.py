import ctypes
from .utils.name import lib_path, sys_type

try:
    LIB = ctypes.CDLL(lib_path) if sys_type != "Windows" else ctypes.cdll.LoadLibrary(lib_path)
except OSError as e:
    raise RuntimeError(f"无法加载 FunCore: {e}") from e
