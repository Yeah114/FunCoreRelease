import threading
import time
import uuid
import queue
import logging
from typing import Callable
from . import FunCore as conn

default_logger = logging.getLogger("conn")
default_logger.setLevel(logging.INFO)
default_console_handler = logging.StreamHandler()
default_console_handler.setLevel(logging.INFO)
default_console_handler.setFormatter(conn.DefaultLoggingFormatter())
default_logger.addHandler(default_console_handler)

class FakeOmega:
    def __init__(self, funcore) -> None:
        self.funcore = funcore

    def get_bot_unique_id(self) -> int:
        return self.funcore.get_bot_unique_id()

class FunCore(conn.GameClient):
    packet_listener: Callable[[int, dict], None] | None = None
    connected = False
    bot_data_ready_event = threading.Event()
    uq_data_ready_event = threading.Event()
    launch_event = threading.Event()
    exit_event = threading.Event()

    def __init__(self, server_code: int = 48285363, server_password: str = "", 
                 auth_server: str = "https://api.nethard.pro", token: str = "", 
                 language: str = "zh_CN", logger = default_logger):
        conn.ChangeLanguage(language)
        self.logger = logger
        self.log = conn.LogClient(self.logger)
        super().__init__(logger = self.logger)
        self.connect(auth_server, token, str(server_code), server_password)
        self.launch_event.set()

    send_command = conn.GameClient.send_player_command_omit_response
    send_ws_command = conn.GameClient.send_websocket_command_omit_response
    send_command_with_response = conn.GameClient.send_player_command_need_response
    send_ws_command_with_response = conn.GameClient.send_websocket_command_need_response

    @property
    def bot_name(self):
        return self.get_bot_name()

    @property
    def bot_uuid(self):
        return self.get_bot_uuid()

    @property
    def bot_xuid(self):
        return self.get_bot_xuid()

    @property
    def bot_unique_id(self):
        return self.get_bot_unique_id()

    @property
    def bot_runtime_id(self):
        return self.get_bot_runtime_id()

    def __del__(self):
        self.disconnect()
        self.exit_event.set()

    # 兼容旧方法的别名
    sendcmd = send_command
    sendwscmd = send_ws_command
    sendwocmd = conn.GameClient.send_settings_command
    sendcmd_with_resp = send_command_with_response
    sendwscmd_with_resp = send_ws_command_with_response
    sendPacket = conn.GameClient.send_game_packet