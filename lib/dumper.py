"""Dump il2cpp file to csharp file."""

import json
import os
import platform
import shutil
from os import path

from lib.downloader import FileDownloader
from utils.util import CommandUtils, FileUtils, ZipUtils
from utils.config import Config
from lib.compiler import CompileToPython, CSParser

def get_platform_identifier():
    os_map = {
        "linux": "linux",
        "darwin": "osx",
        "windows": "win"
    }

    arch_map = {
        "x86_64": "x64",
        "amd64": "x64",
        "arm64": "arm64",
        "aarch64": "arm64"
    }

    os_name = os_map.get(platform.system().lower())
    arch = arch_map.get(platform.machine().lower())

    if not os_name or not arch:
        raise RuntimeError(f"Unsupported OS or architecture: {platform.system()} {platform.machine()}")

    return f"{os_name}-{arch}", os_name

def compile_python(dump_cs_path, extract_dir) -> None:
    """Compile python callable module from dump file"""
    print("Parsing dump.cs...")
    parser = CSParser(dump_cs_path)
    enums = parser.parse_enum()
    structs = parser.parse_struct()
    
    print("Generating flatbuffer python dump files...")
    compiler = CompileToPython(enums, structs, extract_dir)
    compiler.create_enum_files()
    compiler.create_struct_files()
    compiler.create_module_file()
    compiler.create_dump_dict_file()
    compiler.create_repack_dict_file()

class IL2CppDumper:
    def __init__(self) -> None:
        self.project_dir = ""
        self.binary_name = "Il2CppInspector"

    def get_il2cpp_dumper(self, save_path: str) -> None:
        platform_id, os_name = get_platform_identifier()
        
        if Config.server == "CN":
            il2cpp_zip_url = f"https://github.com/beichen23333/cn_metadata_exporter/releases/latest/download/CNMetaExporter-{platform_id}.zip"
            self.binary_name = "cn_metadata_exporter"
        else:
            il2cpp_zip_url = f"https://github.com/beichen23333/Il2CppInspectorRedux/releases/latest/download/Il2CppInspectorRedux.CLI-{platform_id}.zip"
            self.binary_name = "Il2CppInspector"

        zip_path = path.join(save_path, f"{self.binary_name}.zip")
        FileDownloader(il2cpp_zip_url).save_file(zip_path)
        self.project_dir = path.join(save_path, self.binary_name)

        ZipUtils.extract_zip(zip_path, self.project_dir)

        if os_name == "win":
            self.binary_name += ".exe"
        else:
            CommandUtils.run_command(
                "chmod",
                "+x",
                f"./{self.binary_name}",
                cwd=self.project_dir
            )

    def dump_il2cpp(
        self,
        extract_path: str,
        il2cpp_path: str,
        global_metadata_path: str,
        max_retries: int = 1,
    ) -> None:
        os.makedirs(extract_path, exist_ok=True)

        cs_out = path.join(extract_path, "dump.cs")
        binary_path = f"./{self.binary_name}"
        
        if Config.server == "CN":
            success, err = CommandUtils.run_command(
                os.path.abspath(os.path.join(self.project_dir, binary_path)),
                "--metadata", global_metadata_path,
                "--image", "BlueArchive.dll",
                "--output", cs_out,
                cwd=self.project_dir
            )
        else:
            success, err = CommandUtils.run_command(
                os.path.abspath(os.path.join(self.project_dir, binary_path)),
                "--bin", il2cpp_path,
                "--metadata", global_metadata_path,
                "--select-outputs",
                "--cs-out", cs_out,
                "--must-compile",
                cwd=self.project_dir
            )
            
        if not success:
            raise RuntimeError(f"IL2CPP dump failed: {err}")
        return None
