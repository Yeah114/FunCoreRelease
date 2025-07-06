import sys
import os
import importlib
import platform
import getpass
from types import ModuleType

def inject_std_typing():
    # 备份原始路径和模块状态
    original_sys_path = sys.path.copy()
    original_typing_module = sys.modules.get('typing')
    
    # 移除当前目录的干扰
    current_dir = os.getcwd()
    sys.path = [
        p for p in sys.path 
        if p != current_dir and p != "" and not p.endswith(current_dir)
    ]
    
    # 移除现有 typing 模块
    if 'typing' in sys.modules:
        del sys.modules['typing']
    
    try:
        # 加载标准库 typing
        std_typing = importlib.import_module('typing')
        
        # 获取所有成员
        public_members = dir(std_typing)
        
        # 注入全局变量
        globals_dict = globals()
        for name in public_members:
            globals_dict[name] = getattr(std_typing, name)
            
        return True
    finally:
        # 恢复原始环境
        sys.path = original_sys_path
        if original_typing_module is not None:
            sys.modules['typing'] = original_typing_module
        else:
            sys.modules.pop('typing', None)

# 执行注入
inject_std_typing()

# 修改 ToolDelta 逻辑
empty_module = ModuleType("")
sys.modules["tooldelta.internal.launch_cli.fateark_libs.core_conn"] = empty_module # 避免出现 grpcio 错误

# 修改启动器
core_library_file_prefix = "funcore"
sys_machine = platform.machine().lower()
sys_type = platform.system()
arch_map = {"x86_64": "amd64", "aarch64": "arm64"}
sys_machine = arch_map.get(sys_machine, sys_machine)

if sys_type == "Windows":
    lib_name = f"{core_library_file_prefix}_windows_{sys_machine}.dll"
elif "TERMUX_VERSION" in os.environ:
    lib_name = f"{core_library_file_prefix}_android_arm64.so"
elif sys_type == "Linux":
    lib_name = f"{core_library_file_prefix}_linux_{sys_machine}.so"
else:
    lib_name = f"{core_library_file_prefix}_macos_{sys_machine}.dylib"

lib_path = os.path.join("fc_libs", lib_name)

from tooldelta.utils import cfg, urlmethod, sys_args, fbtokenFix, if_token, fmts
from tooldelta.constants import tooldelta_cfg, tooldelta_cli

def load_tooldelta_cfg_and_get_launcher(self):
    """加载配置文件"""
    cfg.write_default_cfg_file("ToolDelta基本配置.json", tooldelta_cfg.LAUNCH_CFG)
    try:
        # 读取配置文件
        cfgs = cfg.get_cfg("ToolDelta基本配置.json", tooldelta_cfg.LAUNCH_CFG_STD)
        self.launchMode = cfgs["启动器启动模式(请不要手动更改此项, 改为0可重置)"]
        self.plugin_market_url = cfgs["插件市场源"]
        fmts.publicLogger.switch_logger(cfgs["是否记录日志"])
    except cfg.ConfigError as err:
        # 配置文件有误
        r = self.upgrade_cfg()
        if r:
            fmts.print_war("配置文件未升级，已自动升级，请重启 ToolDelta")
        else:
            fmts.print_err(f"ToolDelta 基本配置有误，需要更正：{err}")
        raise SystemExit from err
    # 配置全局 GitHub 镜像 URL
    if cfgs["全局GitHub镜像"] == "":
        cfgs["全局GitHub镜像"] = urlmethod.get_fastest_github_mirror()
        if cfgs["插件市场源"] == "":
            cfgs["插件市场源"] = (
                cfgs["全局GitHub镜像"]
                + "/https://raw.githubusercontent.com/ToolDelta-Basic/PluginMarket/main"
            )
        cfg.write_default_cfg_file("ToolDelta基本配置.json", cfgs, True)
    urlmethod.set_global_github_src_url(cfgs["全局GitHub镜像"])
    if not os.path.exists(lib_path):
        fmts.print_inf("开始下载 FunCore 接入点文件")
        url = f'{cfgs["全局GitHub镜像"]}/https://raw.githubusercontent.com/Yeah114/FunCoreRelease/main/fc_libs/{lib_name}'
        url2dst = {
            url: lib_path
        }
        import asyncio
        asyncio.run(urlmethod.download_file_urls(list(url2dst.items())))
    from FunCore import FrameFunCoreLauncher

    launcher = FrameFunCoreLauncher()
    launcher_config_key = "FunCore接入点启动模式"
    launch_data = cfgs.get(
        launcher_config_key, {
            "服务器号": 0,
            "密码": "",
            "验证服务器地址(更换时记得更改fbtoken)": "",
        }
    )
    try:
        cfg.check_auto({
            "服务器号": int,
            "密码": str,
            "验证服务器地址(更换时记得更改fbtoken)": str,
        }, launch_data)
    except cfg.ConfigError as err:
        r = self.upgrade_cfg()
        if r:
            fmts.print_war("配置文件未升级，已自动升级，请重启 ToolDelta")
        else:
            fmts.print_err(
                f"ToolDelta 基本配置-FunCore 启动配置有误，需要更正：{err}"
            )
        raise SystemExit from err

    serverNumber = launch_data["服务器号"]
    serverPasswd: str = launch_data["密码"]
    auth_server = launch_data.get("验证服务器地址(更换时记得更改fbtoken)", "")
    if serverNumber == 0:
        while 1:
            try:
                serverNumber = int(
                    input(fmts.fmt_info("请输入租赁服号：", "§b 输入 "))
                )
                serverPasswd = (
                    getpass.getpass(
                        fmts.fmt_info(
                            "请输入租赁服密码 (不会回显，没有请直接回车): ",
                            "§b 输入 ",
                        )
                    )
                    or ""
                )
                launch_data["服务器号"] = int(serverNumber)
                launch_data["密码"] = serverPasswd
                cfgs[launcher_config_key] = launch_data
                cfg.write_default_cfg_file("ToolDelta基本配置.json", cfgs, True)
                fmts.print_suc("登录配置设置成功")
                break
            except ValueError:
                fmts.print_err("输入有误，租赁服号和密码应当是纯数字")
    auth_servers = tooldelta_cli.AUTH_SERVERS
    if auth_server == "":
        fmts.print_inf("选择 ToolDelta 机器人账号 使用的验证服务器：")
        i = 0
        for i, (auth_server_name, _) in enumerate(auth_servers):
            fmts.print_inf(f" {i + 1} - {auth_server_name}")
        fmts.print_inf(f" {i + 2} - 手动输入")
        fmts.print_inf(
            "§cNOTE: 使用的机器人账号是在哪里获取的就选择哪一个验证服务器，不能混用"
        )
        while 1:
            try:
                ch = int(input(fmts.fmt_info("请选择: ", "§f 输入 ")))
                if ch not in range(1, len(auth_servers) + 1):
                    if ch == len(auth_servers) + 1:
                        auth_server = input(
                            fmts.fmt_info(
                                "请手动输入验证服务器地址: ", "§f 输入 "
                            )
                        )
                        cfgs[launcher_config_key][
                            "验证服务器地址(更换时记得更改fbtoken)"
                        ] = auth_server
                        break
                else:
                    auth_server = auth_servers[ch - 1][1]
                    cfgs[launcher_config_key][
                        "验证服务器地址(更换时记得更改fbtoken)"
                    ] = auth_server
                    break
            except ValueError:
                fmts.print_err("输入不合法，或者是不在范围内，请重新输入")
        cfg.write_default_cfg_file("ToolDelta基本配置.json", cfgs, True)
    # 读取 token
    if not (fbtoken := sys_args.sys_args_to_dict().get("user-token")):
        if not os.path.isfile("fbtoken"):
            fmts.print_inf(
                "请选择登录方法:\n 1 - 使用账号密码获取 fbtoken\n 2 - 手动输入 fbtoken\r"
            )
            login_method = input(fmts.fmt_info("请输入你的选择：", "§6 输入 "))
            while True:
                if login_method.isdigit() is False or int(
                    login_method
                ) not in range(1, 3):
                    login_method = input(
                        fmts.fmt_info(
                            "输入有误, 请输入正确的序号：", "§6 警告 "
                        )
                    )
                else:
                    break
            if login_method == "1":
                try:
                    token = fblike_sign_login(
                        cfgs[launcher_config_key][
                            "验证服务器地址(更换时记得更改fbtoken)"
                        ],
                        tooldelta_cli.FBLIKE_APIS,
                    )
                    with open("fbtoken", "w", encoding="utf-8") as f:
                        f.write(token)
                except requests.exceptions.RequestException as e:
                    fmts.print_err(
                        f"登录失败, 原因: {e}\n请尝试选择手动输入 fbtoken"
                    )
                    raise SystemExit
        if_token()
        fbtokenFix()
        with open("fbtoken", encoding="utf-8") as f:
            fbtoken = f.read()
    
    launcher.serverNumber = serverNumber
    launcher.serverPassword = serverPasswd
    launcher.auth_server_url = auth_server
    launcher.fbToken = fbtoken

    fmts.print_suc("配置文件读取完成")
    return launcher

from tooldelta.internal import config_loader
config_loader.ConfigLoader.load_tooldelta_cfg_and_get_launcher = load_tooldelta_cfg_and_get_launcher