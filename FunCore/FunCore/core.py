import threading
import time
import functools
import json
import uuid as uuid_lib
import nbtlib
import msgpack
from io import BytesIO
from collections import defaultdict
from typing import Optional, Tuple, Callable, Any, List, Dict, DefaultDict, Union

from .go_loader.bind import (
    GameAvailable, ConnectGame, DisconnectGame,
    LogEventPoll, EventPoll, OmitEvent,
    ConsumeCommandResponseCB, ConsumeMCPacket,
    SendWebSocketCommandNeedResponse, SendPlayerCommandNeedResponse,
    SendSettingsCommand, SendTotalSettingsCommand,
    SendWebSocketCommandOmitResponse, SendPlayerCommandOmitResponse,
    ListenAllPackets, GetPacketNameIDMapping, SendGamePacket,
    EnterConsole, PlaceNBTBlockInConsole, GetStructureAsNBT, MoveToPosition,
    GetUQHolderData, GetBotDisplayName, GetBotIdentity, GetBotXUID
)
from .utils.nbt_writer import MarshalPythonNBTObjectToWriter

class Counter:
    """ID生成器，用于创建唯一标识符"""
    def __init__(self, prefix: str) -> None:
        self.current_i = 0
        self.prefix = prefix
        self._lock = threading.Lock()
    
    def __next__(self) -> str:
        """生成下一个唯一ID"""
        with self._lock:
            self.current_i += 1
            return f"{self.prefix}_{self.current_i}"

def check_available(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        first = True
        # 循环检查，直到返回值为 True
        while True:
            status = self.check_available()
            if status:
                break
            if first:
                self.logger.warning(f"FunCore 已与游戏断开连接，{func.__name__} 方法已被暂停")
                first = False
            time.sleep(0.1)
        if not first:
            self.logger.success(f"FunCore 已与游戏恢复连接，{func.__name__} 方法已被恢复")
        # 执行原方法
        return func(self, *args, **kwargs)
    return wrapper

def decorate_core_methods(cls):
    excluded = {"check_available", "connect", "disconnect"}  # 明确排除的方法名
    # 遍历类属性
    for name in cls.__dict__:
        # 跳过以__开头的方法和排除的方法
        if name.startswith("__") or name in excluded:
            continue
        attr = getattr(cls, name)
        # 仅装饰可调用的实例方法
        if callable(attr):
            setattr(cls, name, check_available(attr))
    return cls

# 应用装饰器
@decorate_core_methods
class GameClient:
    """Game 游戏客户端"""
    
    def __init__(self, logger):
        """初始化客户端"""
        self.running = False
        self.event_thread = None
        self.connected = False
        self.logger = logger
        
        # 命令回调系统
        self._cmd_callback_retriever_counter = Counter("cmd_callback")
        self._game_cmd_callback_events: Dict[str, Callable] = {}
        self._callback_lock = threading.Lock()
        
        # 数据包监听系统
        self._packet_name_to_id_mapping: Dict[str, int] = {}
        self._packet_id_to_name_mapping: Dict[int, str] = {}
        self._packet_listeners: DefaultDict[int, set[Callable[[int, Any], None]]] = defaultdict(set)
        self._packet_lock = threading.Lock()
    
    def _create_lock_and_result_setter(self) -> Tuple[Callable, Callable]:
        """
        创建命令响应锁和结果设置器
        
        返回:
            (结果设置器, 结果获取器)
        """
        lock = threading.Lock()
        lock.acquire()
        ret = [None]
        
        def result_setter(result):
            """设置命令响应结果"""
            ret[0] = result
            lock.release()
        
        def result_getter(timeout: int = -1):
            """获取命令响应结果"""
            acquired = lock.acquire(timeout=float(timeout) if timeout >= 0 else -1)
            if acquired:
                lock.release()
            return ret[0]
        
        return result_setter, result_getter
    
    def check_available(self):
        """检查实例是否可用"""
        return GameAvailable()
    
    def connect(
        self,
        auth_server: str,
        auth_token: str,
        server_code: str,
        server_passcode: str,
        console_center_pos: Tuple[int, int, int] = (-30, 0, 30)
    ):
        """
        连接到游戏服务器
        
        参数:
            auth_server: 认证服务器地址
            auth_token: 认证令牌
            server_code: 服务器代码
            server_passcode: 服务器密码
            console_center_pos: 控制台中心位置
            
        异常:
            ConnectionError: 连接失败时抛出
        """
        # 检查现有连接
        if self.connected:
            self.disconnect()
        
        # 建立新连接
        self.auth_server = auth_server
        self.auth_token = auth_token
        self.server_code = server_code
        self.server_passcode = server_passcode
        self.console_center_pos = console_center_pos
        if err := ConnectGame(
            auth_server,
            auth_token,
            server_code,
            server_passcode,
            *console_center_pos
        ):
            raise ConnectionError(f"连接失败: {err}")
        
        # 启动事件处理线程
        self.running = True
        self.connected = True
        self.event_thread = threading.Thread(target=self._react, daemon=True)
        self.event_thread.start()
        
        # 初始化数据包系统
        ListenAllPackets()
        self._packet_name_to_id_mapping = GetPacketNameIDMapping()
        self._packet_id_to_name_mapping = {
            pid: name for name, pid in self._packet_name_to_id_mapping.items()
        }
    
    def disconnect(self):
        """断开游戏连接"""
        if not self.connected:
            return
            
        self.running = False
        self.connected = False
        
        if self.event_thread and self.event_thread.is_alive():
            self.event_thread.join(timeout=2.0)
        
        DisconnectGame()
    
    def _react(self):
        """事件处理主循环"""
        while self.running:
            try:
                event_type, retriever = EventPoll()
                
                if not event_type or not retriever:
                    time.sleep(0.01)
                    continue
                
                if event_type == "CommandResponseCB":
                    self._handle_command_response_cb(retriever)
                elif event_type == "MCPacket":
                    self._handle_mc_packet(retriever)
                else:
                    OmitEvent()
            except Exception as e:
                self.logger.error(f"事件处理错误: {e}")
                time.sleep(0.1)
    
    def _handle_command_response_cb(self, retriever: str):
        """处理命令响应事件"""
        resp = ConsumeCommandResponseCB()
        if resp is None:
            return
            
        try:
            data = json.loads(resp)
        except json.JSONDecodeError:
            data = resp
        
        with self._callback_lock:
            callback = self._game_cmd_callback_events.get(retriever)
        
        if callback:
            try:
                callback(data)
            except Exception as e:
                self.logger.error(f"命令回调处理错误: {e}")
    
    def _handle_mc_packet(self, packet_id_str: str):
        """处理 MC 数据包事件"""
        try:
            packet_id = int(packet_id_str)
        except ValueError:
            OmitEvent()
            return
            
        with self._packet_lock:
            listeners = self._packet_listeners.get(packet_id, set()).copy()
        
        if not listeners:
            OmitEvent()
            return
            
        packet_data_bytes, _, convert_error = ConsumeMCPacket()
        
        if convert_error:
            self.logger.error(f"数据包 {packet_id} 处理出错: {convert_error}")
            return
            
        try:
            # 使用msgpack解析数据包
            packet_data = msgpack.unpackb(packet_data_bytes, strict_map_key=False)
        except Exception as e:
            self.logger.error(f"解析数据包失败: {e}")
            return
            
        for listener in listeners:
            try:
                listener(packet_id, packet_data)
            except Exception as e:
                self.logger.error(f"数据包监听器错误: {e}")
    
    def send_websocket_command_need_response(self, cmd: str, timeout: int = 5) -> Any:
        """
        发送 WebSocket 命令并等待响应
        
        参数:
            cmd: 命令字符串
            timeout: 超时时间(秒)，默认5秒
            
        返回:
            命令响应数据
        """
        setter, getter = self._create_lock_and_result_setter()
        retriever_id = next(self._cmd_callback_retriever_counter)
        
        with self._callback_lock:
            self._game_cmd_callback_events[retriever_id] = setter
        
        try:
            SendWebSocketCommandNeedResponse(cmd, retriever_id)
            return getter(timeout=timeout)
        finally:
            with self._callback_lock:
                if retriever_id in self._game_cmd_callback_events:
                    del self._game_cmd_callback_events[retriever_id]
    
    def send_player_command_need_response(self, cmd: str, timeout: int = 5) -> Any:
        """
        发送 Player 命令并等待响应
        
        参数:
            cmd: 命令字符串
            timeout: 超时时间(秒)，默认5秒
            
        返回:
            命令响应数据
        """
        setter, getter = self._create_lock_and_result_setter()
        retriever_id = next(self._cmd_callback_retriever_counter)
        
        with self._callback_lock:
            self._game_cmd_callback_events[retriever_id] = setter
        
        try:
            SendPlayerCommandNeedResponse(cmd, retriever_id)
            return getter(timeout=timeout)
        finally:
            with self._callback_lock:
                if retriever_id in self._game_cmd_callback_events:
                    del self._game_cmd_callback_events[retriever_id]
    
    def send_settings_command(self, cmd: str):
        """
        发送 WO 命令
        
        参数:
            cmd: 命令字符串
        """
        SendSettingsCommand(cmd)
    
    def send_total_settings_command(self, cmds: str | list) -> bool:
        """
        发送大量 WO 命令
        
        参数:
            cmd: 命令字符串
            
        返回:
            是否成功
        """
        if isinstance(cmds, list):
            cmds = "\n".join(cmds)
        return SendTotalSettingsCommand(cmds)
    
    def send_websocket_command_omit_response(self, cmd: str):
        """
        发送 WebSocket 命令并忽略响应
        
        参数:
            cmd: 命令字符串
        """
        SendWebSocketCommandOmitResponse(cmd)
    
    def send_player_command_omit_response(self, cmd: str):
        """
        发送 Player 命令并忽略响应
        
        参数:
            cmd: 命令字符串
        """
        SendPlayerCommandOmitResponse(cmd)
    
    def send_game_packet(self, packet_id: int, content: Any):
        """
        发送游戏数据包
        
        参数:
            packet_id: 数据包ID
            content: 数据包内容(可序列化为JSON)
        """        
        if error := SendGamePacket(packet_id, json.dumps(content)):
            raise RuntimeError(f"发送数据包失败: {error}")
    
    def add_packets_listener(
        self,
        targets: int | List[int],
        callback: Callable[[int, Any], None]
    ):
        """
        添加数据包监听器
        
        参数:
            targets: 目标数据包ID或列表
            callback: 回调函数，参数为(数据包ID, 数据包内容)
        """
        if isinstance(targets, int):
            targets = [targets]
        with self._packet_lock:
            for t in targets:
                self._packet_listeners[t].add(callback)
    
    def remove_packet_listener(
        self,
        packet_id: int,
        callback: Callable[[int, Any], None]
    ):
        """
        移除指定数据包监听器
        
        参数:
            packet_id: 目标数据包ID
            callback: 要移除的回调函数
        """
        with self._packet_lock:
            if packet_id in self._packet_listeners:
                self._packet_listeners[packet_id].discard(callback)
    
    def remove_all_listeners(self):
        """移除所有数据包监听器"""
        with self._packet_lock:
            self._packet_listeners.clear()
    
    def get_uqholder_data(self) -> dict | None:
        """
        获取 UQHolder 数据
        
        返回:
            UQHolder 数据
        """
        uqholder_data_bytes, _, marshal_error = GetUQHolderData()
        if marshal_error:
            self.logger.error(f"获取 UQHolder 失败: {marshal_error}")
            return
        if uqholder_data_bytes is None:
            return
        
        uqholder_data = {k: msgpack.unpackb(v, strict_map_key=False) for k, v in msgpack.unpackb(uqholder_data_bytes).items()}
        players_info_holder_data = {}
        for uuid, player in uqholder_data["PlayersInfoHolder"].items():
            player["UUID"] = uuid_lib.UUID(bytes=uuid)
            players_info_holder_data[uuid_lib.UUID(bytes=uuid)] = player
        uqholder_data["PlayersInfoHolder"] = players_info_holder_data

        return uqholder_data
    
    def get_players_info(self) -> Optional[dict]:
        """获取 UQHolder 里的 PlayersInfoHolder"""
        uqholder_data = self.get_uqholder_data()
        if uqholder_data is None:
            return None
        return uqholder_data.get("PlayersInfoHolder")
    
    def get_bot_basic_info(self) -> Optional[dict]:
        """获取 UQHolder 里的 BotBasicInfoHolder"""
        uqholder_data = self.get_uqholder_data()
        if uqholder_data is None:
            return None
        return uqholder_data.get("BotBasicInfoHolder")
    
    def get_extend_info(self) -> Optional[dict]:
        """获取 UQHolder 里的 ExtendInfo"""
        uqholder_data = self.get_uqholder_data()
        if uqholder_data is None:
            return None
        return uqholder_data.get("ExtendInfo")
    
    def get_bot_name(self) -> str | None:
        """获取机器人的名称"""
        return GetBotDisplayName()

    def get_bot_uuid(self) -> str | None:
        """获取机器人的 UUID"""
        return GetBotIdentity()

    def get_bot_xuid(self) -> str | None:
        """获取机器人的 XUID"""
        return GetBotXUID()

    def get_bot_runtime_id(self) -> int | None:
        """获取机器人的 RuntimeID"""
        bot_basic_info = self.get_bot_basic_info()
        if bot_basic_info is None:
            return None
        return bot_basic_info.get("BotRuntimeID")
    
    def get_bot_unique_id(self) -> int | None:
        """获取机器人的 UniqueID"""
        bot_basic_info = self.get_bot_basic_info()
        if bot_basic_info is None:
            return None
        return bot_basic_info.get("BotUniqueID")

    @property
    def uqs(self):
        """获取以玩家名字为键名的玩家 UQHolder 数据"""
        players_info = self.get_players_info()
        if players_info is None:
            return None
        _uqs = {}
        for _, player_data in players_info.items():
            _uqs[player_data["Username"]] = player_data
        
        return _uqs
    
    def place_nbt_block_in_console(
        self,
        block_name: str,
        block_states: str,
        block_nbt: bytes | nbtlib.tag.Compound
    ) -> Tuple[bool, str, Tuple[int, int, int], Optional[str]]:
        """
        在控制台放置NBT方块
        
        参数:
            block_name: 要放置的方块名字
            block_states: 要放置的方块状态
            block_nbt: 要放置的方块 NBT
        
        返回:
            (是否可快速放置, 唯一ID, (x偏移, y偏移, z偏移), 错误信息)
        """
        if isinstance(block_nbt, nbtlib.tag.Compound):
            block_nbt_buffer = BytesIO()
            MarshalPythonNBTObjectToWriter(block_nbt_buffer, block_nbt, "")
            block_nbt_bytes = block_nbt_buffer.getvalue()
        else:
            block_nbt_bytes = block_nbt
        return PlaceNBTBlockInConsole(block_name, block_states, block_nbt_bytes)
    
    def place_nbt_block_in_world(
        self,
        block_name: str,
        block_states: str,
        block_nbt: bytes | nbtlib.tag.Compound,
        block_pos: Tuple[int, int, int]
    ) -> Optional[str]:
        """
        使用控制台在世界放置 NBT 方块
        
        参数:
            block_name: 要放置的方块名字
            block_states: 要放置的方块状态
            block_nbt: 要放置的方块 NBT
            block_pos: 要放置的坐标
        
        返回:
            错误信息
        """
        err = self.enter_console()
        if err:
            return err
        
        can_fast, _, offset, err = self.place_nbt_block_in_console(block_name, block_states, block_nbt)
        if err:
            return err
    
        # 创建坐标计算辅助函数
        def offset_pos(base_pos, offset):
            return [base_pos[i] + offset[i] for i in range(3)]
        
        console_pos = offset_pos(self.console_center_pos, offset)
        console_pos_str = f"{console_pos[0]} {console_pos[1]} {console_pos[2]}"
        block_pos_str = f"{block_pos[0]} {block_pos[1]} {block_pos[2]}"
        tp_console_cmd = f"/tp @s {console_pos_str}"
        tp_world_cmd = f"/tp @s {block_pos_str}"
        
        # 统一命令执行和错误检查
        def execute_command(cmd):
            result = self.send_websocket_command_need_response(cmd)
            if not result or not result["OutputMessages"][0]["Success"]:
                return f"发送 WebSocket 命令失败 ({cmd})"
            return None
    
        if can_fast:
            # 快速模式：传送+setblock
            if err := execute_command(tp_world_cmd):
                return err
            
            setblock_cmd = f"/setblock {block_pos_str} {block_name} {block_states}"
            if err := execute_command(setblock_cmd):
                # 这是不要紧的，因为那个地方可能已经有了相同方块，而导致无法放置
                # return err
                pass
            return None
    
        # 结构模式：传送+保存结构+加载结构
        if err := execute_command(tp_console_cmd):
            return err
    
        structure_save_cmd = (
            f'/structure save "place_nbt_block_in_world" '
            f'{console_pos_str} '
            f'{console_pos_str} false memory true'
        )
        if err := execute_command(structure_save_cmd):
            return err
    
        # 确保结构被删除（使用try-finally保证资源清理）
        try:
            if err := execute_command(tp_world_cmd):
                return err
    
            structure_load_cmd = f'/structure load "place_nbt_block_in_world" {block_pos_str}'
            if err := execute_command(structure_load_cmd):
                return err
        finally:
            structure_delete_cmd = '/structure delete "place_nbt_block_in_world"'
            result = self.send_websocket_command_need_response(structure_delete_cmd)
            if not result or not result["OutputMessages"][0]["Success"]:
                # 记录删除失败但不中断主流程
                self.logger.warning(f"结构删除失败 ({structure_delete_cmd})")
    
        return None
    
    def get_structure_as_nbt(self, origin, size):
        """
        获取一个结构 NBT
        
        参数:
            origin: 结构在世界的坐标
            size: 结构的大小
        
        返回:
            NBT 字节
        """
        structure_nbt_data_bytes, _, convert_error = GetStructureAsNBT(*origin, *size)
        if convert_error:
            self.logger.error(f"结构 NBT 处理出错: {convert_error}")
            return
        return structure_nbt_data_bytes

    def move_to_pos(self, pos, facing):
        return MoveToPosition(
            pos[0],
            pos[1],
            pos[2],
            facing[0],
            facing[1],
            facing[2]
        )

    def enter_console(self):
        """
        进入控制台
        
        返回:
            错误信息
        """
        return EnterConsole()

class LogClient:
    """Game 日志处理客户端"""
    
    def __init__(self, logger):
        """初始化日志客户端"""
        self.logger = logger
        if not hasattr(self.logger, "success"):
            self.logger.success = self.logger.info
        self.event_thread = threading.Thread(target=self._react, daemon=True)
        self.event_thread.start()
        self.log_callback: Optional[Callable[[str, str], Tuple[str, str]]] = None

    def _react(self):
        while True:
            level, message = LogEventPoll()
            if not level or not message:
                time.sleep(0.01)
                continue
                
            level = level.upper()
            if self.log_callback:
                level, message = self.log_callback(level, message)
                
            if level == "TRACE":
                self.logger.info(message)
            elif level == "DEBUG":
                self.logger.debug(message)
            elif level == "INFO":
                self.logger.info(message)
            elif level == "WARN":
                self.logger.warning(message)
            elif level == "ERROR":
                self.logger.error(message)
            elif level == "FATAL":
                self.logger.critical(message)
            elif level == "UNKNOWN":
                self.logger.info(message)
