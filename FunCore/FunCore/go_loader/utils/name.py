import os
import platform

core_library_file_prefix = "funcore"
sys_machine = platform.machine().lower()
sys_type = platform.system()
arch_map = {"x86_64": "amd64", "aarch64": "arm64"}
sys_machine = arch_map.get(sys_machine, sys_machine)

if sys_type == "Windows":
    lib_path = f"{core_library_file_prefix}_windows_{sys_machine}.dll"
elif "TERMUX_VERSION" in os.environ:
    lib_path = f"{core_library_file_prefix}_android_arm64.so"
elif sys_type == "Linux":
    lib_path = f"{core_library_file_prefix}_linux_{sys_machine}.so"
else:
    lib_path = f"{core_library_file_prefix}_macos_{sys_machine}.dylib"

lib_path = os.path.join("fc_libs", lib_path)
