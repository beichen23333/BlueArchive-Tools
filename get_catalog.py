import os
import dotenv

from argparse import ArgumentParser
from lib.downloader import FileDownloader
from lib.console import notice
from utils.config import Config
from utils.util import ZipUtils
from xtractor.catalog import CatalogMemoryPack, CNMXCatalog

def parse_args():
    p = ArgumentParser(description="维护更新")
    p.add_argument("server", type=str, choices=["CN", "GL", "JP"], help="服务器区域")
    p.add_argument("type", type=str, choices=["Media", "Table", "Bundle"], help="资源类型")
    p.add_argument("client", type=str, choices=["Android", "iOS", "Windows"], help="客户端平台")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    Config.server = args.server

    dotenv.load_dotenv(f"BA_{Config.server}.env")
    base_url = os.getenv('AddressableCatalogUrl')

    download_url = ""
    os.makedirs("Download", exist_ok=True)

    if args.type == "Media":
        input_file = "MediaCatalog.bytes"
        if Config.server == "JP":
            res_path = "MediaResources-Windows" if args.client == "Windows" else "MediaResources"
            download_url = f"{base_url}/{res_path}/Catalog/MediaCatalog.bytes"

        elif Config.server == "GL":
            download_url = f"{base_url}/Catalog/MediaResources/MediaCatalog.bytes"

        elif Config.server == "CN":
            media_ver = os.getenv('MediaVersion')
            manifest_path = "Download/MediaManifest"
            
            FileDownloader(url=f"{base_url}/Manifest/MediaResources/{media_ver}/MediaManifest", verbose=False).save_file(manifest_path)
            
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_content = f.read()
            
            catalog = CNMXCatalog(manifest_content)
            manifest_json = catalog.parse_media_manifest()
            
            with open("Download/MediaCatalog.json", "w", encoding="utf-8") as f:
                f.write(manifest_json)

    elif args.type == "Bundle":
        input_file = "BundlePackingInfo.bytes"
        if Config.server == "JP":
            download_url = f"{base_url}/{args.client}_PatchPack/BundlePackingInfo.bytes"
            if args.client != "Windows":
                zip_name = f"catalog_{args.client}.zip"
                zip_path = f"Download/{zip_name}"
                FileDownloader(url=f"{base_url}/{args.client}_PatchPack/{zip_name}").save_file(zip_path)
                ZipUtils.extract_zip(zip_path, "Download")

        elif Config.server == "GL":
            if args.client == "Android":
                FileDownloader(url=os.getenv('ServerInfoDataUrl'), verbose=False).save_file("Download/BundlePackingInfo.json")

        elif Config.server == "CN":
            if args.client != "Windows":
                res_ver = os.getenv('ResourceVersion')
                FileDownloader(url=f"{base_url}/AssetBundles/Catalog/{res_ver}/{args.client}/bundleDownloadInfo.json", verbose=False).save_file("Download/BundlePackingInfo.json")

    elif args.type == "Table":
        input_file = "TableCatalog.bytes"
        if Config.server == "JP":
            download_url = f"{base_url}/TableBundles/TableCatalog.bytes"

        elif Config.server == "GL":
            download_url = f"{base_url}/Catalog/TableBundles/TableCatalog.bytes"

        elif Config.server == "CN":
            table_ver = os.getenv('TableVersion')
            FileDownloader(url=f"{base_url}/Manifest/TableBundles/{table_ver}/TableManifest", verbose=False).save_file("Download/TableCatalog.json")

    if download_url:
        FileDownloader(url=download_url).save_file(f"Download/{input_file}")

        if Config.server != "CN":
            CatalogMemoryPack_obj = CatalogMemoryPack()
            CatalogMemoryPack_obj.get_catalog_memory_pack("Temp")

            abs_input_path = os.path.abspath(f"Download/{input_file}")
            abs_output_path = os.path.abspath(input_file.replace(".bytes", ".json"))

            success, error_msg = CatalogMemoryPack_obj.run(
                server=Config.server,
                mode="deserialize",
                catalog_type=args.type,
                input_path=abs_input_path,
                output_path=abs_output_path
            )
            if not success:
                print(f"执行出错：{error_msg}")
