import io
import struct
import json
import os
from utils.util import CommandUtils, ZipUtils
from lib.dumper import get_platform_identifier
from lib.downloader import FileDownloader

class MXCatalogReader:
    """
    根据 beichen23333/BAAD 项目内service/MXCatalog.java改写。
    功能一致，用于转换MemoryPack序列化后的Catalog。

    使用例子
    catalog = MXCatalogReader.parse_jp(data,"Media")
    catalog.MediaCatalog()

    因限制，该类仅能用于提取做解析测试而无法写回。
    如需写回Catalog，请使用CatalogMemoryPack。
    """
    @staticmethod
    def readU64(dis):
        return struct.unpack('<Q', dis.read(8))[0]

    @staticmethod
    def readBool(dis):
        return struct.unpack('<?', dis.read(1))[0]

    @staticmethod
    def readString(dis):
        length = MXCatalogReader.readI32(dis)
        if length < -1:
            length = MXCatalogReader.readI32(dis)
        return dis.read(length).decode('utf-8') if length > 0 else ""

    @staticmethod
    def readStringList(dis):
        size = MXCatalogReader.readI32(dis)
        if size < -1:
            size = MXCatalogReader.readI32(dis)
        return [MXCatalogReader.readString(dis) for _ in range(size)]

    @staticmethod
    def readI32(dis):
        return struct.unpack('<i', dis.read(4))[0]

    @staticmethod
    def readI64(dis):
        return struct.unpack('<q', dis.read(8))[0]

    @staticmethod
    def parse_jp(bytesData, Type):
        dis = io.BytesIO(bytesData)
        dis.read(1)
        catalog = JPMXCatalog()
        if Type == "Table":
            catalog.Table = MXCatalogReader.readTableBundles_jp(dis)
            catalog.TablePack = MXCatalogReader.readTablePatchPacks_jp(dis)
        elif Type == "Media":
            catalog.Table = MXCatalogReader.readMedia_jp(dis)
        elif Type == "Bundle":
            catalog.Milestone = MXCatalogReader.readString(dis)
            catalog.PatchVersion = MXCatalogReader.readI32(dis)
            catalog.FullPatchPacks = MXCatalogReader.readBundlePatchPack_jp(dis)
            catalog.UpdatePacks = MXCatalogReader.readBundlePatchPack_jp(dis)
        return catalog

    @staticmethod
    def readTableBundles_jp(dis):
        # Table包结构
        count = MXCatalogReader.readI32(dis)
        result = {}
        for _ in range(count):
            key = MXCatalogReader.readString(dis)
            dis.read(1)
            result[key] = {
                "Name": MXCatalogReader.readString(dis),
                "Size": MXCatalogReader.readI64(dis),
                "Crc": MXCatalogReader.readU64(dis),
                "isInbuild": MXCatalogReader.readBool(dis),
                "isChanged": MXCatalogReader.readBool(dis),
                "IsPrologue": MXCatalogReader.readBool(dis),
                "IsSplitDownload": MXCatalogReader.readBool(dis),
                "Includes": MXCatalogReader.readStringList(dis)
            }
        return result

    @staticmethod
    def readTablePatchPacks_jp(dis):
        # TablePack包结构
        count = MXCatalogReader.readI32(dis)
        result = {}
        for _ in range(count):
            key = MXCatalogReader.readString(dis)
            dis.read(1)
            item = {
                "Name": MXCatalogReader.readString(dis),
                "Size": MXCatalogReader.readI64(dis),
                "Crc": MXCatalogReader.readU64(dis),
                "IsPrologue": MXCatalogReader.readBool(dis)
            }
            arraySize = MXCatalogReader.readI32(dis)
            item["BundleFiles"] = []
            for _ in range(arraySize):
                dis.read(1)
                item["BundleFiles"].append({
                    "Name": MXCatalogReader.readString(dis),
                    "Size": MXCatalogReader.readI64(dis),
                    "Crc": MXCatalogReader.readU64(dis),
                    "isInbuild": MXCatalogReader.readBool(dis),
                    "isChanged": MXCatalogReader.readBool(dis),
                    "IsPrologue": MXCatalogReader.readBool(dis),
                    "IsSplitDownload": MXCatalogReader.readBool(dis),
                    "Includes": MXCatalogReader.readStringList(dis)
                })
            result[key] = item
        return result

    @staticmethod
    def readMedia_jp(dis):
        # Media包结构
        count = MXCatalogReader.readI32(dis)
        result = {}
        for _ in range(count):
            MXCatalogReader.readString(dis)
            dis.read(1)
            path = MXCatalogReader.readString(dis).replace('\\', '/')
            item = {
                "Path": path,
                "FileName": MXCatalogReader.readString(dis),
                "Bytes": MXCatalogReader.readI64(dis),
                "Crc": MXCatalogReader.readU64(dis),
                "IsPrologue": MXCatalogReader.readBool(dis),
                "IsSplitDownload": MXCatalogReader.readBool(dis),
                "MediaType": MXCatalogReader.readI32(dis)
            }
            result[item["Path"]] = item
        return result

    @staticmethod
    def readBundlePatchPack_jp(dis):
        # Bundle里面的两个结构相同
        count = MXCatalogReader.readI32(dis)
        result = {}
        for _ in range(count):
            dis.read(1)
            item = {
                "PackName": MXCatalogReader.readString(dis),
                "PackSize": MXCatalogReader.readI64(dis),
                "Crc": MXCatalogReader.readU64(dis),
                "IsPrologue": MXCatalogReader.readBool(dis),
                "IsSplitDownload": MXCatalogReader.readBool(dis)
            }
            bundleFilesCount = MXCatalogReader.readI32(dis)
            item["BundleFiles"] = [
                {
                    "Name": (dis.read(1), MXCatalogReader.readString(dis))[1],
                    "Size": MXCatalogReader.readI64(dis),
                    "IsPrologue": MXCatalogReader.readBool(dis),
                    "Crc": MXCatalogReader.readU64(dis),
                    "IsSplitDownload": MXCatalogReader.readBool(dis),
                    "FileHash": MXCatalogReader.readU64(dis),
                    "Signature": MXCatalogReader.readString(dis)
                }
                for _ in range(bundleFilesCount)
            ]
            result[item["PackName"]] = item
        return result

class MXCatalog:
    def TableCatalog(self):
        return {
            "Table": {
                k: {
                    "Name": v["Name"],
                    "Size": v["Size"],
                    "Crc": v["Crc"],
                    "isInbuild": v["isInbuild"],
                    "isChanged": v["isChanged"],
                    "IsPrologue": v["IsPrologue"],
                    "IsSplitDownload": v["IsSplitDownload"],
                    "Includes": v["Includes"]
                } for k, v in self.Table.items()
            },
            "TablePack": {
                k: {
                    "Name": v["Name"],
                    "Size": v["Size"],
                    "Crc": v["Crc"],
                    "IsPrologue": v["IsPrologue"],
                    "BundleFiles": [
                        {
                            "Name": b["Name"],
                            "Size": b["Size"],
                            "Crc": b["Crc"],
                            "isInbuild": b["isInbuild"],
                            "isChanged": b["isChanged"],
                            "IsPrologue": b["IsPrologue"],
                            "IsSplitDownload": b["IsSplitDownload"],
                            "Includes": b["Includes"]
                        } for b in v["BundleFiles"]
                    ]
                } for k, v in self.TablePack.items()
            }
        }

    def MediaCatalog(self):
        return {
            "Table": {
                k: {
                    "Path": v["Path"],
                    "FileName": v["FileName"],
                    "Bytes": v["Bytes"],
                    "Crc": v["Crc"],
                    "IsPrologue": v["IsPrologue"],
                    "IsSplitDownload": v["IsSplitDownload"],
                    "MediaType": v["MediaType"]
                } for k, v in self.Table.items()
            }
        }

    def BundlePackingInfo(self):
        return {
            "Milestone": self.Milestone,
            "PatchVersion": self.PatchVersion,
            "FullPatchPacks": {
                k: {
                    "PackName": v["PackName"],
                    "PackSize": v["PackSize"],
                    "Crc": v["Crc"],
                    "IsPrologue": v["IsPrologue"],
                    "IsSplitDownload": v["IsSplitDownload"],
                    "BundleFiles": [
                        {
                            "Name": b["Name"],
                            "Size": b["Size"],
                            "IsPrologue": b["IsPrologue"],
                            "Crc": b["Crc"],
                            "IsSplitDownload": b["IsSplitDownload"],
                            "FileHash": b["FileHash"],
                            "Signature": b["Signature"]
                        } for b in v["BundleFiles"]
                    ]
                } for k, v in self.FullPatchPacks.items()
            },
            "UpdatePacks": {
                k: {
                    "PackName": v["PackName"],
                    "PackSize": v["PackSize"],
                    "Crc": v["Crc"],
                    "IsPrologue": v["IsPrologue"],
                    "IsSplitDownload": v["IsSplitDownload"],
                    "BundleFiles": [
                        {
                            "Name": b["Name"],
                            "Size": b["Size"],
                            "IsPrologue": b["IsPrologue"],
                            "Crc": b["Crc"],
                            "IsSplitDownload": b["IsSplitDownload"],
                            "FileHash": b["FileHash"],
                            "Signature": b["Signature"]
                        } for b in v["BundleFiles"]
                    ]
                } for k, v in self.UpdatePacks.items()
            }
        }


class CNMXCatalog:
    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.media_type = {
            0: "none",
            1: "ogg",
            2: "mp4",
            3: "jpg",
            4: "png",
            5: "acb",
            6: "awb"
        }

    def parse_media_manifest(self):
        lines = self.raw_data.strip().split('\n')
        result = {}
        for line in lines:
            if not line.strip():
                continue

            parts = [p.strip() for p in line.rstrip(',').split(',')]

            if len(parts) >= 4:
                # 为确保Key值唯一，故此进行文件后缀拼接
                raw_key = parts[0]
                m_type_value = int(parts[2])
                media_type = self.media_type.get(m_type_value, str(m_type_value))
                unique_key = f"{raw_key}.{media_type}"            
                result[unique_key] = {
                    "Hash": parts[1],
                    "MediaType": media_type,
                    "Size": int(parts[3])
                }
        return json.dumps(result, indent=4, ensure_ascii=False)

class CatalogMemoryPack:
    def __init__(self):
        self.project_dir = ""
        self.binary_name = "MemoryPackRepacker"

    def run(
        self, 
        server: str, 
        mode: str, 
        catalog_type: str, 
        input_path: str, 
        output_path: str
    ) -> tuple[bool, str]:
        """
        执行 MemoryPackRepacker
        
        Args:
            server: 服务器类型（JP / GL）
            mode: 模式 （serialize / deserialize）
            catalog_type: catalog类型 （Media / Table / Bundle(国际服不需要解密)）
            input_path: 输入文件路径
            output_path: 输出文件路径
        """

        commands = [
            f"./{self.binary_name}",
            server,
            mode,
            catalog_type,
            input_path,
            output_path
        ]

        success, error_msg = CommandUtils.run_command(*commands, cwd=self.project_dir)
        
        if success:
            print(f"[{server.upper()} | {catalog_type}] {mode.capitalize()} Success.")
        else:
            print(f"Operation failed: {error_msg}")
            
        return success, error_msg

    def get_catalog_memory_pack(self, save_path: str) -> None:
        platform_id, os_name = get_platform_identifier()
        catalog_zip_url = f"https://github.com/beichen23333/CatalogMemoryPack/releases/latest/download/MemoryPackRepacker-{platform_id}.zip"
        os.makedirs(save_path, exist_ok=True)
        zip_path = os.path.join(save_path, "CatalogMemoryPack.zip")
        FileDownloader(catalog_zip_url).save_file(zip_path)
        self.project_dir = os.path.join(save_path, "CatalogMemoryPack")

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


