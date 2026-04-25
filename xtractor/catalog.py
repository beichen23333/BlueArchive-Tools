import io
import struct
import json

"""
使用例子
catalog = MXCatalogReader.parse(data,"Media")
catalog.MediaCatalog()
"""

class MXCatalogReader:
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
    def parse(bytesData, Type):
        dis = io.BytesIO(bytesData)
        dis.read(1)
        catalog = MXCatalog()
        if Type == "Table":
            catalog.Table = MXCatalogReader.readTableBundles(dis)
            catalog.TablePack = MXCatalogReader.readTablePatchPacks(dis)
        elif Type == "Media":
            catalog.Table = MXCatalogReader.readMedia(dis)
        elif Type == "Bundle":
            catalog.Milestone = MXCatalogReader.readString(dis)
            catalog.PatchVersion = MXCatalogReader.readI32(dis)
            catalog.FullPatchPacks = MXCatalogReader.readBundlePatchPack(dis)
            catalog.UpdatePacks = MXCatalogReader.readBundlePatchPack(dis)
        return catalog

    @staticmethod
    def readTableBundles(dis):
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
    def readTablePatchPacks(dis):
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
    def readMedia(dis):
        # Media包结构
        count = MXCatalogReader.readI32(dis)
        result = {}
        for _ in range(count):
            MXCatalogReader.readString(dis)
            dis.read(1)
            item = {
                "Path": MXCatalogReader.readString(dis),
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
    def readBundlePatchPack(dis):
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

