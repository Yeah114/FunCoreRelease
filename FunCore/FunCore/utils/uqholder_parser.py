import struct
import uuid as uuid_lib
from io import BytesIO
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional, BinaryIO

class UQHolderParser:
    """解析 UQHolder 数据的类"""
    
    @staticmethod
    def parse_bool(reader: BinaryIO) -> bool:
        """解析布尔值"""
        data = reader.read(1)
        if not data:
            raise EOFError("Unexpected EOF reading bool")
        return data != b'\x00'

    @staticmethod
    def parse_uint8(reader: BinaryIO) -> int:
        """解析 8 位无符号整数"""
        data = reader.read(1)
        if not data:
            raise EOFError("Unexpected EOF reading uint8")
        return data[0]

    @staticmethod
    def parse_int16(reader: BinaryIO) -> int:
        """解析 16 位有符号整数"""
        data = reader.read(2)
        if not data or len(data) < 2:
            raise EOFError("Unexpected EOF reading int16")
        return struct.unpack('<h', data)[0]

    @staticmethod
    def parse_uint16(reader: BinaryIO) -> int:
        """解析 16 位无符号整数"""
        data = reader.read(2)
        if not data or len(data) < 2:
            raise EOFError("Unexpected EOF reading uint16")
        return struct.unpack('<H', data)[0]

    @staticmethod
    def parse_int32(reader: BinaryIO) -> int:
        """解析 32 位有符号整数"""
        data = reader.read(4)
        if not data or len(data) < 4:
            raise EOFError("Unexpected EOF reading int32")
        return struct.unpack('<i', data)[0]

    @staticmethod
    def parse_uint32(reader: BinaryIO) -> int:
        """解析 32 位无符号整数"""
        data = reader.read(4)
        if not data or len(data) < 4:
            raise EOFError("Unexpected EOF reading uint32")
        return struct.unpack('<I', data)[0]

    @staticmethod
    def parse_int64(reader: BinaryIO) -> int:
        """解析 64 位有符号整数"""
        data = reader.read(8)
        if not data or len(data) < 8:
            raise EOFError("Unexpected EOF reading int64")
        return struct.unpack('<q', data)[0]

    @staticmethod
    def parse_uint64(reader: BinaryIO) -> int:
        """解析 64 位无符号整数"""
        data = reader.read(8)
        if not data or len(data) < 8:
            raise EOFError("Unexpected EOF reading uint64")
        return struct.unpack('<Q', data)[0]

    @staticmethod
    def parse_float32(reader: BinaryIO) -> float:
        """解析 32 位浮点数"""
        data = reader.read(4)
        if not data or len(data) < 4:
            raise EOFError("Unexpected EOF reading float32")
        return struct.unpack('<f', data)[0]

    @staticmethod
    def parse_float64(reader: BinaryIO) -> float:
        """解析 64 位浮点数"""
        data = reader.read(8)
        if not data or len(data) < 8:
            raise EOFError("Unexpected EOF reading float64")
        return struct.unpack('<d', data)[0]

    @staticmethod
    def parse_string(reader: BinaryIO) -> str:
        """解析 UTF-8 字符串"""
        length = UQHolderParser.parse_uint16(reader)
        if length > 32767:  # math.MaxInt16
            raise ValueError(f"String length {length} exceeds maximum 32767")
        data = reader.read(length)
        if len(data) != length:
            raise EOFError(f"Unexpected EOF reading string, expected {length} bytes, got {len(data)}")
        return data.decode('utf-8')

    @staticmethod
    def parse_uuid(reader: BinaryIO) -> uuid_lib.UUID:
        """解析 UUID (16 字节)"""
        data = reader.read(16)
        if len(data) != 16:
            raise EOFError("Unexpected EOF reading UUID")
        return uuid_lib.UUID(bytes=data)

    @classmethod
    def parse_extend_info(cls, data: bytes) -> Dict[str, Any]:
        """解析 ExtendInfoHolder 结构"""
        reader = BytesIO(data)
        result = {}
        
        result["CompressThreshold"] = cls.parse_uint16(reader)
        result["knownCompressThreshold"] = cls.parse_bool(reader)
        
        result["CurrentTick"] = cls.parse_int64(reader)
        result["knownCurrentTick"] = cls.parse_bool(reader)
        
        result["syncRatio"] = cls.parse_float32(reader)
        
        result["WorldGameMode"] = cls.parse_int32(reader)
        result["knownWorldGameMode"] = cls.parse_bool(reader)
        
        result["WorldDifficulty"] = cls.parse_uint32(reader)
        result["knownWorldDifficulty"] = cls.parse_bool(reader)
        
        result["Time"] = cls.parse_int32(reader)
        result["knownTime"] = cls.parse_bool(reader)
        
        result["DayTime"] = cls.parse_int32(reader)
        result["knownDayTime"] = cls.parse_bool(reader)
        
        result["DayTimePercent"] = cls.parse_float32(reader)
        result["knownDayTimePercent"] = cls.parse_bool(reader)
        
        game_rule_count = cls.parse_uint32(reader)
        game_rules = {}
        for _ in range(game_rule_count):
            key = cls.parse_string(reader)
            can_be_modified = cls.parse_bool(reader)
            value = cls.parse_string(reader)
            game_rules[key] = {
                "CanBeModifiedByPlayer": can_be_modified,
                "Value": value
            }
        result["GameRules"] = game_rules
        result["knownGameRules"] = cls.parse_bool(reader)
        
        result["Dimension"] = cls.parse_int32(reader)
        result["knownDimension"] = cls.parse_bool(reader)
        
        result["botRuntimeIDDup"] = cls.parse_uint64(reader)
        
        result["PositionUpdateTick"] = cls.parse_int64(reader)
        
        position = [
            cls.parse_float32(reader),
            cls.parse_float32(reader),
            cls.parse_float32(reader)
        ]
        result["Position"] = position
        
        result["currentContainerOpened"] = cls.parse_bool(reader)
        if result["currentContainerOpened"]:
            container = {}
            container["WindowID"] = cls.parse_uint8(reader)
            container["ContainerType"] = cls.parse_uint8(reader)
            container["ContainerPosition"] = [
                cls.parse_int32(reader),
                cls.parse_int32(reader),
                cls.parse_int32(reader)
            ]
            container["ContainerEntityUniqueID"] = cls.parse_int64(reader)
            result["currentOpenedContainer"] = container
        
        if reader.read(1):
            raise ValueError("Extra data in ExtendInfoHolder")
        
        return result

    @classmethod
    def parse_bot_basic_info(cls, data: bytes) -> Dict[str, Any]:
        """解析 BotBasicInfoHolder 结构"""
        reader = BytesIO(data)
        result = {}
        
        result["BotName"] = cls.parse_string(reader)
        result["BotRuntimeID"] = cls.parse_uint64(reader)
        result["BotUniqueID"] = cls.parse_int64(reader)
        result["BotIdentity"] = cls.parse_string(reader)
        
        if reader.read(1):
            raise ValueError("Extra data in BotBasicInfoHolder")
        
        return result

    @classmethod
    def parse_player(cls, data: bytes) -> Dict[str, Any]:
        """解析 Player 结构"""
        reader = BytesIO(data)
        result = {}
        total_len = len(data)
        
        result["UUID"] = cls.parse_uuid(reader)
        result["knownUUID"] = cls.parse_bool(reader)
        
        result["EntityUniqueID"] = cls.parse_int64(reader)
        result["knownEntityUniqueID"] = cls.parse_bool(reader)
        
        result["NeteaseUID"] = cls.parse_int64(reader)
        result["knownNeteaseUID"] = cls.parse_bool(reader)
        
        login_timestamp = cls.parse_int64(reader)
        result["LoginTime"] = datetime.fromtimestamp(login_timestamp)
        result["knownLoginTime"] = cls.parse_bool(reader)
        
        result["Username"] = cls.parse_string(reader)
        result["knownUsername"] = cls.parse_bool(reader)
        
        result["XUID"] = cls.parse_string(reader)
        result["knownXUID"] = cls.parse_bool(reader)
        
        result["PlatformChatID"] = cls.parse_string(reader)
        result["knownPlatformChatID"] = cls.parse_bool(reader)
        
        result["BuildPlatform"] = cls.parse_int32(reader)
        result["knownBuildPlatform"] = cls.parse_bool(reader)
        
        result["SkinID"] = cls.parse_string(reader)
        result["knownSkinID"] = cls.parse_bool(reader)
        
        # 解析能力标志和状态标志
        result["knowAbilitiesAndStatus"] = cls.parse_bool(reader)
        
        # 8 个能力标志
        result["canBuild"] = cls.parse_bool(reader)
        result["canMine"] = cls.parse_bool(reader)
        result["canDoorsAndSwitches"] = cls.parse_bool(reader)
        result["canOpenContainers"] = cls.parse_bool(reader)
        result["canAttackPlayers"] = cls.parse_bool(reader)
        result["canAttackMobs"] = cls.parse_bool(reader)
        result["canOperatorCommands"] = cls.parse_bool(reader)
        result["canTeleport"] = cls.parse_bool(reader)
        
        # 3 个状态标志
        result["statusInvulnerable"] = cls.parse_bool(reader)
        result["statusFlying"] = cls.parse_bool(reader)
        result["statusMayFly"] = cls.parse_bool(reader)
        
        result["DeviceID"] = cls.parse_string(reader)
        result["knownDeviceID"] = cls.parse_bool(reader)
        
        result["EntityRuntimeID"] = cls.parse_uint64(reader)
        result["knownEntityRuntimeID"] = cls.parse_bool(reader)
        
        result["knownEntityMetadata"] = cls.parse_bool(reader)
        result["EntityMetadata"] = None
        
        result["Online"] = cls.parse_bool(reader)
        return result

    @classmethod
    def parse_players(cls, data: bytes) -> Dict[str, Any]:
        """解析 Players 结构（包含多个 Player）"""
        reader = BytesIO(data)
        result = {"players": []}
        
        player_count = cls.parse_uint32(reader)
        for _ in range(player_count):
            data_len = cls.parse_uint32(reader)
            player_data = reader.read(data_len)
            if len(player_data) != data_len:
                raise EOFError(f"Unexpected EOF reading player data, expected {data_len} bytes, got {len(player_data)}")
            player = cls.parse_player(player_data)
            result["players"].append(player)
        
        if reader.read(1):
            raise ValueError("Extra data in Players")
        
        return result

    @classmethod
    def parse_uqholder(cls, data: bytes) -> Dict[str, bytes]:
        """解析顶层 UQHolder 结构"""
        reader = BytesIO(data)
        result = {}
        
        modules = ["ExtendInfo", "BotBasicInfoHolder", "PlayersInfoHolder"]
        for _ in modules:
            module_name = cls.parse_string(reader)
            if module_name not in modules:
                raise ValueError(f"Nonexistent module: {module_name}")
            
            subdata_len = cls.parse_int64(reader)
            subdata = reader.read(subdata_len)
            if len(subdata) != subdata_len:
                raise EOFError(f"Unexpected EOF reading {module_name} data")
            result[module_name] = subdata
        
        if reader.read(1):
            raise ValueError("Extra data detected after parsing")
        
        return result

    @classmethod
    def parse_full(cls, data: bytes) -> Dict[str, Any]:
        """解析完整的 UQHolder 数据"""
        top_level = cls.parse_uqholder(data)
        result = {}
        
        if "BotBasicInfoHolder" in top_level:
            bot_data = top_level["BotBasicInfoHolder"]
            result["BotBasicInfo"] = cls.parse_bot_basic_info(bot_data)
        
        if "PlayersInfoHolder" in top_level:
            players_data = top_level["PlayersInfoHolder"]
            result["PlayersInfo"] = cls.parse_players(players_data)
        
        if "ExtendInfo" in top_level:
            extend_data = top_level["ExtendInfo"]
            result["ExtendInfo"] = cls.parse_extend_info(extend_data)
        
        return result

uqholder_parser = UQHolderParser()