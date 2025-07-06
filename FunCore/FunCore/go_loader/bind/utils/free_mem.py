from .init import LIB, CPointer

LIB.FreeMem.argtypes = [CPointer]
def FreeMem(pointer: CPointer):
    """释放内存指针"""
    if pointer:
        LIB.FreeMem(pointer)
