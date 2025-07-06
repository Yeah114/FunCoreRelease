import ctypes

# Go语言数据类型别名
GoInt = ctypes.c_longlong
GoInt32 = ctypes.c_int
CString = ctypes.c_char_p
GoBool = ctypes.c_bool
GoFloat32 = ctypes.c_float
CStructure = ctypes.Structure
CBytes = ctypes.POINTER(ctypes.c_char)
CPointer = ctypes.c_void_p