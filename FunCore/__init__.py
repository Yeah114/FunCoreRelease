import os
import time
import threading
from . import core_conn as funcore_conn
from tooldelta.utils import fmts
from tooldelta.internal.types import *
from tooldelta.packets import Packet_CommandOutput
from tooldelta.constants import SysStatus
from tooldelta.internal.launch_cli.standard_launcher import StandardFrame

class LikeFmtsLogger:
    def __init__(self):
        self.info = fmts.print_inf
        self.debug = fmts.print_inf
        self.warning = fmts.print_war
        self.error = fmts.print_err
        self.critical = fmts.print_err
    

class FrameFunCoreLauncher(StandardFrame):
    # 启动器类型
    launch_type = "FunCore"

    def launch(self) -> SystemExit:
        """启动器启动

        Raises:
            SystemError: 无法启动此启动器
        """
        self.update_status(SysStatus.LAUNCHING)
        fmts.print_inf("正在连接到FunCore...")
        self.funcore = funcore_conn.FunCore(
            server_code=self.serverNumber,
            server_password=self.serverPassword,
            auth_server=self.auth_server_url,
            token=self.fbToken,
            language="zh_CN",
            logger=LikeFmtsLogger()
        )
        self.bot_name = self.funcore.bot_name
        self.omega = funcore_conn.FakeOmega(self.funcore)
        self.update_status(SysStatus.RUNNING)
        self.funcore.add_packets_listener(list(self.need_listen_packets), self.packet_handler_parent)
        self._exec_launched_listen_cbs()
        self.funcore.exit_event.wait()
        self.update_status(SysStatus.NORMAL_EXIT)
        return SystemExit("FunCore 和 ToolDelta 断开连接")

    def get_players_and_uuids(self) -> dict[str, str]:
        """获取玩家名和 UUID"""
        return {k: v['UUID'] for k, v in self.funcore.uqs.items()}

    def get_bot_name(self) -> str:
        """获取机器人名字"""
        return self.funcore.bot_name

    def packet_handler_parent(self, pkt_type: int, pkt: dict) -> None:
        """数据包处理器

        Args:
            pkt_type (str): 数据包类型
            pkt (dict): 数据包内容

        Raises:
            ValueError: 还未连接到游戏
        """
        if not self.funcore.connected:
            raise ValueError("还未连接到游戏")
        self.dict_packet_handler(pkt_type, pkt)

    def sendcmd(
        self, cmd: str, waitForResp: bool = False, timeout: float = 30
    ) -> Packet_CommandOutput | None:
        """以玩家身份发送命令

        Args:
            cmd (str): 命令
            waitForResp (bool, optional): 是否等待结果
            timeout (int | float, optional): 超时时间

        Raises:
            TimeoutError: 获取命令返回超时

        Returns:
            Packet_CommandOutput: 返回命令结果
        """
        if not waitForResp:
            self.funcore.sendcmd(cmd)
        else:
            if (res := self.funcore.sendcmd_with_resp(cmd, timeout)):
                return Packet_CommandOutput(res)
            else:
                raise TimeoutError("获取命令返回超时")

    def sendwscmd(
        self, cmd: str, waitForResp: bool = False, timeout: float = 30
    ) -> Packet_CommandOutput | None:
        """以 ws 身份发送命令

        Args:
            cmd (str): 命令
            waitForResp (bool, optional): 是否等待结果
            timeout (int | float, optional): 超时时间

        Raises:
            TimeoutError: 获取命令返回超时

        Returns:
            Packet_CommandOutput: 返回命令结果
        """
        if not waitForResp:
            self.funcore.sendwscmd(cmd)
        else:
            if (res := self.funcore.sendwscmd_with_resp(cmd, timeout)):
                return Packet_CommandOutput(res)
            else:
                raise TimeoutError("获取命令返回超时")

    def sendwocmd(self, cmd: str) -> None:
        """以 wo 身份发送命令

        Args:
            cmd (str): 命令

        """
        self.funcore.sendwocmd(cmd)

    def sendPacket(self, pckID: int, pck: dict) -> None:
        """发送数据包

        Args:
            pckID (int): 数据包 ID
            pck (str): 数据包内容

        """
        self.funcore.sendPacket(pckID, pck)

    sendPacketJson = sendPacket

    def is_op(self, player: str) -> bool:
        """检查玩家是否为 OP

        Args:
            player (str): 玩家名

        Returns:
            bool: 是否为 OP
        """
        if player not in self.funcore.uqs.keys():
            raise ValueError(f"玩家不存在: {player}")
        return self.funcore.uqs[player]["canOperatorCommands"]

    def get_players_info(self):
        players_data: dict[str, UnreadyPlayer] = {}
        for i in self.funcore.uqs.values():
            if i is not None:
                ab = Abilities(
                    build = i["canBuild"],
                    mine = i["canMine"],
                    doors_and_switches = i["canDoorsAndSwitches"],
                    open_containers = i["canOpenContainers"],
                    attack_players = i["canAttackPlayers"],
                    attack_mobs = i["canAttackMobs"],
                    operator_commands = i["canOperatorCommands"],
                    teleport = i["canTeleport"],
                    player_permissions = 0,
                    command_permissions = 3 if i["canOperatorCommands"] else 1,
                )
                players_data[i["Username"]] = UnreadyPlayer(
                    uuid = str(i["UUID"]),
                    xuid = i["XUID"],
                    unique_id = i["EntityUniqueID"],
                    name = i["Username"],
                    device_id = ["DeviceID"],
                    platform_chat_id = i["PlatformChatID"],
                    build_platform = i["BuildPlatform"],
                    abilities = ab,
                    online = True,
                )
            else:
                raise ValueError("未能获取玩家名和 UUID")
        return players_data
