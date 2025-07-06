import logging

class DefaultLoggingFormatter(logging.Formatter):
    """自定义日志格式化器，支持彩色输出"""
    
    # ANSI 颜色和样式代码
    GREY = "\033[1;30m"    # 加粗灰色
    GREEN = "\033[1;32m"   # 加粗绿色
    YELLOW = "\033[1;33m"  # 加粗黄色
    RED = "\033[1;31m"     # 加粗红色
    BOLD_RED = "\033[1;37;41m"  # 加粗白色文字+红色背景
    RESET = "\033[0m"      # 重置样式
    
    # 日志级别固定宽度（8字符）
    LEVEL_WIDTH = 8
    
    def __init__(self):
        super().__init__()
        self.date_fmt = "%Y-%m-%d %H:%M:%S"
        
    def format(self, record):
        # 创建固定宽度的日志级别（加粗）
        levelname = record.levelname
        padded_level = f"{levelname:^{self.LEVEL_WIDTH}}"  # 居中填充
        
        color = self.get_color(record.levelno)
        # 创建基础日志格式
        log_line = f"\033[36m{self.formatTime(record, self.date_fmt)} {color}{padded_level}{self.RESET} {record.getMessage()}"
        
        return log_line
    
    def get_color(self, levelno):
        """获取日志级别对应的颜色"""
        if levelno >= logging.CRITICAL:
            return self.BOLD_RED
        elif levelno >= logging.ERROR:
            return self.RED
        elif levelno >= logging.WARNING:
            return self.YELLOW
        elif levelno >= logging.INFO:
            return self.GREEN
        else:  # DEBUG
            return self.GREY