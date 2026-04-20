import json
import multiprocessing
import multiprocessing.queues
import multiprocessing.synchronize
import os
import stat
import struct
import subprocess
import tempfile
from os import path
from typing import Any, Literal, List, Optional, Union

from PIL import Image
from lib.console import ProgressBar
from crcmanip.crc import CRC32
from crcmanip.algorithm import apply_patch, consume

# ---------------------------------------------------------------------------
# tools/UABEA/UABEAvalonia
# ---------------------------------------------------------------------------
_UABEA_DIR = path.join(path.dirname(path.dirname(path.abspath(__file__))), "tools", "UABEA")
_UABEA_BIN = path.join(_UABEA_DIR, "UABEAvalonia")


class BundleExtractor:
    UABEA_CLI: str = _UABEA_BIN

    MAIN_EXTRACT_TYPES = [
        "Texture2D", "Sprite", "AudioClip", "Font", "TextAsset",
        "Mesh", "VideoClip", "MonoBehaviour", "Shader",
    ]

    def __init__(self, EXTRACT_DIR: str = "output", BUNDLE_FOLDER: str = "") -> None:
        self.BUNDLE_FOLDER = BUNDLE_FOLDER
        self.BUNDLE_EXTRACT_FOLDER = EXTRACT_DIR
        self._ensure_uabea_executable()

    # ------------------------------------------------------------------
    # UABEA CLI 基础设施
    # ------------------------------------------------------------------

    def _ensure_uabea_executable(self) -> None:
        if path.exists(self.UABEA_CLI) and not os.access(self.UABEA_CLI, os.X_OK):
            os.chmod(self.UABEA_CLI,
                     os.stat(self.UABEA_CLI).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    def _run_uabea(self, args: List[str]) -> subprocess.CompletedProcess:
        """
        执行 UABEAvalonia CLI 命令。
        文件路径参数需用绝对路径传入（本函数内自动转换 -f/-d/-o/-i/-b/-a 后面跟的路径）。
        cwd 保持为 UABEA 二进制目录，以确保 TexturePlugin.dll 等插件能被正确加载。
        """
        # 将路径参数自动转为绝对路径
        abs_args: List[str] = []
        path_flags = {"-f", "-d", "-o", "-i", "-b", "-a"}
        i = 0
        while i < len(args):
            abs_args.append(args[i])
            if args[i] in path_flags and i + 1 < len(args):
                i += 1
                abs_args.append(os.path.abspath(args[i]))
            i += 1

        cmd = [self.UABEA_CLI] + abs_args
        try:
            return subprocess.run(cmd, capture_output=True, text=True, cwd=_UABEA_DIR)
        except Exception as e:
            return subprocess.CompletedProcess(cmd, returncode=-1, stdout="", stderr=str(e))

    @staticmethod
    def _parse_list_output(output: str) -> List[dict]:
        """解析 ``UABEAvalonia list`` 的 stdout，返回资源描述 dict 列表。"""
        assets: List[dict] = []
        current_source = ""
        is_bundle = False

        for line in output.splitlines():
            s = line.strip()
            if s.startswith("Bundle:"):
                current_source = s.split(":", 1)[1].strip()
                is_bundle = True
                continue
            if s.startswith("Assets File:"):
                current_source = s.split(":", 1)[1].split("(")[0].strip()
                is_bundle = False
                continue
            if not s or s.startswith("-") or s.startswith("PathID") or s.startswith("Total"):
                continue
            cols = s.split()
            try:
                int(cols[0])
            except (ValueError, IndexError):
                continue

            if is_bundle and len(cols) >= 5:
                assets.append({
                    "path_id": cols[0], "entry": cols[1], "type": cols[2],
                    "size": cols[3], "name": " ".join(cols[4:]),
                    "source_path": current_source,
                })
            elif not is_bundle and len(cols) >= 4:
                entry_name = os.path.basename(current_source) if current_source else ""
                assets.append({
                    "path_id": cols[0], "entry": entry_name, "type": cols[1],
                    "size": cols[2], "name": " ".join(cols[3:]),
                    "source_path": current_source,
                })
        return assets

    # ------------------------------------------------------------------
    # 兼容层：_MockReadData / _MockObj（保持调用方不变）
    # ------------------------------------------------------------------

    class _MockReadData:
        """模拟 UnityPy obj.read() 的返回对象。"""
        def __init__(self, asset_info: dict, raw_bytes: Optional[bytes] = None) -> None:
            self._info = asset_info
            self.m_Name: str = asset_info.get("name", "")
            self._raw = raw_bytes
            # UABEA raw 导出的 TextAsset 包含 Unity 序列化头部：
            #   int32  m_Name 长度
            #   char[] m_Name
            #   padding (对齐到 4 字节)
            #   int32  m_Script 长度
            #   byte[] m_Script 实际内容
            # 需要剥离头部，只保留 m_Script 数据，与 UnityPy 行为一致。
            if raw_bytes and asset_info.get("type") == "TextAsset":
                self.m_Script = self._parse_textasset_raw(raw_bytes)
            else:
                self.m_Script: str = (
                    raw_bytes.decode("utf-8", "surrogateescape") if raw_bytes else ""
                )
            self.bundleVersion: str = ""

        @staticmethod
        def _parse_textasset_raw(raw: bytes) -> str:
            """从 UABEA raw 导出的 TextAsset 二进制中提取 m_Script 内容。"""
            import struct
            try:
                if len(raw) < 4:
                    return raw.decode("utf-8", "surrogateescape")
                # 读取 m_Name 长度
                name_len = struct.unpack_from("<i", raw, 0)[0]
                # 合理性检查：名称长度应在 0~1024 之间
                if not (0 <= name_len <= 1024) or 4 + name_len > len(raw):
                    return raw.decode("utf-8", "surrogateescape")
                # 跳过 m_Name + 对齐填充
                offset = 4 + name_len
                offset = (offset + 3) & ~3  # 对齐到 4 字节边界
                # 读取 m_Script 长度
                if offset + 4 > len(raw):
                    return raw.decode("utf-8", "surrogateescape")
                script_len = struct.unpack_from("<i", raw, offset)[0]
                offset += 4
                if not (0 <= script_len <= len(raw) - offset):
                    return raw.decode("utf-8", "surrogateescape")
                # 提取 m_Script 数据
                script_bytes = raw[offset:offset + script_len]
                return script_bytes.decode("utf-8", "surrogateescape")
            except Exception:
                return raw.decode("utf-8", "surrogateescape")

        def __getattr__(self, item: str) -> Any:
            return ""

    class _MockObj:
        """模拟 UnityPy 对象，兼容 .read()、.source_path、.type.name 等访问。"""
        class _Type:
            def __init__(self, name: str) -> None:
                self.name = name

        def __init__(self, asset_info: dict, read_data: "BundleExtractor._MockReadData") -> None:
            self._info = asset_info
            self._read_data = read_data
            self.source_path: str = asset_info.get("source_path", "")
            self.path_id: str = asset_info.get("path_id", "")
            self.type = BundleExtractor._MockObj._Type(asset_info.get("type", ""))

        def read(self) -> "BundleExtractor._MockReadData":
            return self._read_data

    # ------------------------------------------------------------------
    # search_unity_pack — CLI list（目录并发，单文件顺序）
    # ------------------------------------------------------------------

    def search_unity_pack(
        self,
        pack_path: str,
        data_type: Optional[List[str]] = None,
        data_name: Optional[List[str]] = None,
        condition_connect: bool = False,
        read_obj_anyway: bool = False,
        _workers: int = 8,
    ) -> List[Any]:
        """
        在 bundle 文件（或目录）中搜索匹配的 Unity 资源，返回兼容 UnityPy 的 _MockObj 列表。

        目录模式下使用 list -d 一次性搜索；单文件模式使用 list -f。
        """
        # ── 目录：使用 list -d 一次性搜索，避免逐文件启动子进程 ───────────
        if os.path.isdir(pack_path):
            list_args = ["list", "-d", pack_path, "--recursive"]
            if data_type:
                list_args += ["-t", ",".join(data_type)]
            if data_name and (condition_connect or read_obj_anyway):
                list_args += ["-n", ",".join(f"={n}" for n in data_name)]

            result = self._run_uabea(list_args)
            if result.returncode != 0:
                return []

            candidates = self._parse_list_output(result.stdout)
            data_list: List[Any] = []

            for info in candidates:
                info.setdefault("source_path", pack_path)
                type_passed = (not data_type) or (info["type"] in data_type)
                name_passed = (not data_name) or (info["name"] in data_name)

                if condition_connect or read_obj_anyway:
                    if not (type_passed and name_passed):
                        continue
                else:
                    if not type_passed:
                        continue

                # TextAsset：导出原始内容以填充 m_Script
                raw_bytes: Optional[bytes] = None
                if info["type"] == "TextAsset":
                    source_file = info.get("source_path", "")
                    if source_file:
                        with tempfile.TemporaryDirectory() as tmp_dir:
                            exp = self._run_uabea([
                                "export", "-f", source_file,
                                "-p", info["path_id"],
                                "-o", tmp_dir, "--format", "raw",
                            ])
                            if exp.returncode == 0:
                                for fname in os.listdir(tmp_dir):
                                    fpath = path.join(tmp_dir, fname)
                                    if path.isfile(fpath):
                                        with open(fpath, "rb") as fh:
                                            raw_bytes = fh.read()
                                        break

                read_data = BundleExtractor._MockReadData(info, raw_bytes)
                data_list.append(BundleExtractor._MockObj(info, read_data))

            return data_list

        list_args = ["list", "-f", pack_path]
        if data_type:
            list_args += ["-t", ",".join(data_type)]
        if data_name and (condition_connect or read_obj_anyway):
            list_args += ["-n", ",".join(f"={n}" for n in data_name)]

        result = self._run_uabea(list_args)
        if result.returncode != 0:
            return []

        candidates = self._parse_list_output(result.stdout)
        data_list = []

        for info in candidates:
            info.setdefault("source_path", pack_path)
            type_passed = (not data_type) or (info["type"] in data_type)
            name_passed = (not data_name) or (info["name"] in data_name)

            if condition_connect or read_obj_anyway:
                if not (type_passed and name_passed):
                    continue
            else:
                if not type_passed:
                    continue

            raw_bytes: Optional[bytes] = None
            if info["type"] == "TextAsset":
                with tempfile.TemporaryDirectory() as tmp_dir:
                    exp = self._run_uabea([
                        "export", "-f", pack_path,
                        "-p", info["path_id"],
                        "-o", tmp_dir, "--format", "raw",
                    ])
                    if exp.returncode == 0:
                        for fname in os.listdir(tmp_dir):
                            fpath = path.join(tmp_dir, fname)
                            if path.isfile(fpath):
                                with open(fpath, "rb") as fh:
                                    raw_bytes = fh.read()
                                break

            read_data = BundleExtractor._MockReadData(info, raw_bytes)
            data_list.append(BundleExtractor._MockObj(info, read_data))

        return data_list

    # ------------------------------------------------------------------
    # Unity SerializedFile 安全 CRC 修补位置
    # ------------------------------------------------------------------

    @staticmethod
    def _find_safe_patch_position(file_path: str) -> Optional[int]:
        """
        在 Unity SerializedFile 的 metadata↔data 填充区中找到一个安全的
        4 字节覆写位置，用于 CRC 修补。

        Unity SerializedFile 的布局：
          [header | metadata | padding… | data section]
        其中 *data_offset* 指向数据段起始偏移。padding 区域全为 0x00，
        覆写其中的 4 字节不会影响任何 Unity 对象的读取。

        如果不是 SerializedFile 或没有足够的 padding，返回 None。
        """
        try:
            with open(file_path, 'rb') as f:
                header = f.read(48)
            if len(header) < 20:
                return None
            # 排除 AssetBundle 格式（UnityFS / UnityWeb / UnityRaw）
            if header[:7] in (b'UnityFS', b'UnityWe', b'UnityRa'):
                return None
            # format version 固定位于 offset 8 (uint32 big-endian)
            version = struct.unpack_from('>I', header, 8)[0]
            if version < 9:
                return None
            # 根据版本号获取 data_offset
            if version >= 22:
                # v22+: data_offset 为 int64 BE，位于 offset 0x20
                if len(header) < 0x28:
                    return None
                data_offset = struct.unpack_from('>q', header, 0x20)[0]
            else:
                # v9~v21: data_offset 为 uint32 BE，位于 offset 12
                data_offset = struct.unpack_from('>I', header, 12)[0]
            file_size = os.path.getsize(file_path)
            # 使用 padding 区域末尾 4 字节（紧邻 data section 之前）
            safe_pos = data_offset - 4
            if safe_pos >= 28 and data_offset <= file_size:
                return safe_pos
            return None
        except Exception:
            return None

    def _patch_crc(self, filepath: str, original_crc: int) -> None:
        """
        在不破坏 Unity 资产数据的前提下修补文件的 CRC。
        
        通过在文件末尾追加 4 字节补丁，使文件整体 CRC 恢复到修改前的值。
        """
        # 读取经 UABEA 修改后的文件数据
        with open(filepath, "rb") as f:
            data = f.read()
        
        input_io = io.BytesIO(data)
        output_io = io.BytesIO()
        file_size = len(data)

        codec = CRC32()
        # 计算并应用补丁，在当前文件末尾 (target_pos=file_size) 增加字节
        apply_patch(
            crc=codec,
            target_checksum=original_crc,
            input_handle=input_io,
            output_handle=output_io,
            target_pos=file_size,
            overwrite=False
        )

        # 将修补后的数据写回原文件
        with open(filepath, "wb") as f:
            f.write(output_io.getvalue())

    # ------------------------------------------------------------------
    # modify_and_replace — CLI import + CRC/Size 修补
    # ------------------------------------------------------------------

    @staticmethod
    def _new_data_to_file(
        obj_type: str,
        new_data: Any,
        asset_name: str,
        entry: str,
        path_id: str,
        tmp_dir: str,
    ) -> Optional[str]:
        """
        将 new_data 写入 tmp_dir，文件名符合 UABEA 导入规则：
            {AssetName}-{entry}-{PathID}.{ext}
        返回写入的完整路径；若类型不支持则返回 None（不回退UnityPy）。
        """
        stem = f"{asset_name}-{entry}-{path_id}" if entry else f"{asset_name}-{path_id}"

        if obj_type == "TextAsset":
            fpath = path.join(tmp_dir, stem + ".txt")
            if isinstance(new_data, str):
                raw = new_data.encode("utf-8", "surrogateescape")
            else:
                raw = bytes(new_data)
            with open(fpath, "wb") as f:
                f.write(raw)
            return fpath

        if obj_type == "Texture2D":
            if isinstance(new_data, Image.Image):
                fpath = path.join(tmp_dir, stem + ".png")
                new_data.save(fpath)
                return fpath
            if isinstance(new_data, (bytes, list)):
                fpath = path.join(tmp_dir, stem + ".dat")
                with open(fpath, "wb") as f:
                    f.write(bytes(new_data) if isinstance(new_data, list) else new_data)
                return fpath

        if obj_type == "Font" and isinstance(new_data, (bytes, list)):
            raw = bytes(new_data) if isinstance(new_data, list) else new_data
            ext = ".otf" if raw[:4] == b"OTTO" else ".ttf"
            fpath = path.join(tmp_dir, stem + ext)
            with open(fpath, "wb") as f:
                f.write(raw)
            return fpath

        if obj_type == "VideoClip" and isinstance(new_data, (bytes, list)):
            fpath = path.join(tmp_dir, stem + ".dat")
            with open(fpath, "wb") as f:
                f.write(bytes(new_data) if isinstance(new_data, list) else new_data)
            return fpath

        if obj_type == "MonoBehaviour" and isinstance(new_data, dict):
            fpath = path.join(tmp_dir, stem + ".json")
            with open(fpath, "wt", encoding="utf-8") as f:
                json.dump(new_data, f, ensure_ascii=False, indent=2)
            return fpath

        # AudioClip 等暂不支持，返回 None
        return None

    def modify_and_replace(self, folder_path: str, asset_name: str, new_data: Any) -> None:
        if os.path.isdir(folder_path):
            list_result = self._run_uabea([
                "list", "-d", folder_path, "-n", f"={asset_name}", "--recursive",
            ])
            if list_result.returncode != 0:
                return
            all_matches = [
                m for m in self._parse_list_output(list_result.stdout)
                if m["name"] == asset_name
            ]
            if not all_matches:
                return
            # 按文件去重，每个文件只处理第一个匹配
            seen_files: set = set()
            for match in all_matches:
                filepath = match.get("source_path", "")
                if filepath and filepath not in seen_files:
                    seen_files.add(filepath)
                    self._import_single_asset(filepath, match, asset_name, new_data)
        else:
            list_result = self._run_uabea([
                "list", "-f", folder_path, "-n", f"={asset_name}",
            ])
            if list_result.returncode != 0:
                return
            matches = [
                m for m in self._parse_list_output(list_result.stdout)
                if m["name"] == asset_name
            ]
            if not matches:
                return
            self._import_single_asset(folder_path, matches[0], asset_name, new_data)

    def _import_single_asset(
        self,
        filepath: str,
        match: dict,
        asset_name: str,
        new_data: Any,
    ) -> None:
        """将单个资源写入指定 bundle 文件，并修补 CRC/Size。"""
        try:
            # ── 1. 获取原始文件的 CRC32 值 (整数形式) ──────────────────────
            codec = CRC32()
            with open(filepath, "rb") as f:
                consume(codec, f)
            original_crc_int = codec.digest()

            obj_type = match["type"]
            entry = match["entry"]
            path_id = match["path_id"]

            # ── 2. 将 new_data 写入临时目录 ────────────────────────────────
            with tempfile.TemporaryDirectory() as tmp_dir:
                import_file = self._new_data_to_file(
                    obj_type, new_data, asset_name, entry, path_id, tmp_dir
                )
                if import_file is None:
                    # 这里回退逻辑删除，不再使用UnityPy
                    return

                # ── 3. UABEA import 写回 ──────────────────────────────────
                imp = self._run_uabea(["import", "-f", filepath, "-i", tmp_dir])
                if imp.returncode != 0:
                    return

            # ── 4. CRC 修补 (使用原始 CRC 整数值) ─────────────────────────
            self._patch_crc(filepath, original_crc_int)

        except Exception:
            pass

    # ------------------------------------------------------------------
    # extract_bundle — UABEA CLI export（Step 3）
    # ------------------------------------------------------------------

    # UABEA 导出格式映射
    _EXPORT_FORMAT: dict = {
        "Texture2D": "png",
        "Sprite":    "png",
        "AudioClip": "wav",
        "TextAsset": "raw",
        "Font":      "raw",
        "VideoClip": "raw",
        "Mesh":      "raw",
        "MonoBehaviour": "json",
        "Shader":    "raw",
    }

    @staticmethod
    def _strip_uabea_suffix(filename: str) -> str:
        """
        去除 UABEA 导出文件名中的 -{entry}-{PathID} 后缀，还原为资源名。
        例: "Arial-sharedassets0-123.dat" → "Arial.dat"
        """
        stem, _, ext = filename.rpartition(".")
        # 去掉末尾两段 "-xxx"（PathID + entry）
        parts = stem.rsplit("-", 2)
        if len(parts) == 3:
            return parts[0] + "." + ext
        if len(parts) == 2:
            # assets 文件：只有 PathID
            return parts[0] + "." + ext
        return filename

    def extract_bundle(self, res_path: str, extract_types: Optional[List[str]] = None) -> None:
        """
        使用 UABEA CLI export 提取资源到 BUNDLE_EXTRACT_FOLDER/{Type}/ 目录。
        支持单文件（-f）和目录批量模式（-d --recursive）。
        """
        types_to_extract = extract_types or self.MAIN_EXTRACT_TYPES
        is_dir = os.path.isdir(res_path)
        path_flag = "-d" if is_dir else "-f"

        for obj_type in types_to_extract:
            fmt = self._EXPORT_FORMAT.get(obj_type, "raw")
            extract_folder = path.join(self.BUNDLE_EXTRACT_FOLDER, obj_type)
            os.makedirs(extract_folder, exist_ok=True)

            with tempfile.TemporaryDirectory() as tmp_dir:
                export_args = [
                    "export", path_flag, res_path,
                    "-t", obj_type,
                    "-o", tmp_dir,
                    "--format", fmt,
                ]
                if is_dir:
                    export_args.append("--recursive")

                result = self._run_uabea(export_args)
                if result.returncode != 0:
                    continue

                for fname in os.listdir(tmp_dir):
                    src = path.join(tmp_dir, fname)
                    if not path.isfile(src):
                        continue
                    clean_name = self._strip_uabea_suffix(fname)
                    dst = path.join(extract_folder, clean_name)
                    # 避免同名覆盖（取第一个）
                    if not path.exists(dst):
                        import shutil
                        shutil.move(src, dst)

    # ------------------------------------------------------------------
    # multiprocess_extract_worker — 直接调用 UABEA CLI export -d（Step 4）
    # ------------------------------------------------------------------

    def multiprocess_extract_worker(self, tasks: multiprocessing.Queue, extract_types: Optional[List[str]]) -> None:
        """
        消费 tasks 队列中的 bundle 路径，逐个调用 extract_bundle。
        （UABEA CLI 本身已足够快，多进程只用于并行处理多文件。）
        """
        while not tasks.empty():
            try:
                bundle_path = tasks.get_nowait()
                ProgressBar.item_text(path.basename(bundle_path))
                self.extract_bundle(bundle_path, extract_types)
            except Exception:
                pass
