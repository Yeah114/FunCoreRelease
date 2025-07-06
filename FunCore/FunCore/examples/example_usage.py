import logging
from FunCore import GameClient, LogClient, DefaultLoggingFormatter, ChangeLanguage

if __name__ == "__main__":
    # 初始化日志
    ChangeLanguage("zh_CN")
    logger = logging.getLogger("conn")
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(DefaultLoggingFormatter())
    logger.addHandler(console_handler)
    
    # 创建日志客户端
    log_client = LogClient(logger)
    
    # 创建游戏客户端
    client = GameClient(logger=logger)
    
    try:
        # 连接到租赁服
        client.connect(
            auth_server="...",
            auth_token="...",
            server_code="...",
            server_passcode="..."
        )
        
        # 发送测试命令
        print("\n发送命令: /list")
        cmd_resp1 = client.send_websocket_command_need_response("/list")
        print(f"命令返回: {cmd_resp1}")
        
        print("\n发送命令: /say Hello from FunCore!")
        cmd_resp2 = client.send_websocket_command_need_response("/say Hello from FunCore!")
        print(f"命令返回: {cmd_resp2}")
        
        # 获取玩家信息
        players_info = client.get_players_info()
        print(f"\n在线玩家: {[p['Username'] for p in players_info['players']]}")
        
        # 获取机器人信息
        bot_name = client.get_bot_name()
        bot_runtime_id = client.get_bot_runtime_id()
        print(f"\n机器人信息: {bot_name} (RuntimeID: {bot_runtime_id})")
        
    except Exception as e:
        logger.error(f"发生错误: {e}")
    finally:
        # 断开连接
        client.disconnect()