from .init import LIB, CString, toCString

LIB.ChangeLanguage.argtypes = [CString]
def ChangeLanguage(language = "zh_CN"):
    """切换语言"""
    LIB.ChangeLanguage(toCString(language))
