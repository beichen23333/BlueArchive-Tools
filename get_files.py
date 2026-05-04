import os
import json
import dotenv
from argparse import ArgumentParser
from lib.downloader import FileDownloader
from utils.config import Config

def parse_args():
    p = ArgumentParser(description="维护更新")
    p.add_argument("server", type=str, choices=["CN", "GL", "JP"], help="服务器区域")
    p.add_argument("type", type=str, choices=["Media", "Table", "Bundle"], help="资源类型")
    p.add_argument("client", type=str, choices=["Android", "iOS", "Windows"], help="客户端平台")
    p.add_argument("-f", "--files", nargs="+", help="控制下载的文件名列表")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    Config.server = args.server

    dotenv.load_dotenv(f"BA_{Config.server}.env")
    base_url = os.getenv('AddressableCatalogUrl')

    os.makedirs("Download_Temp", exist_ok=True)

    download_list = []
    if args.files:
        if Config.server == "JP":
            for file_name in args.files:
                if args.type == "Table":
                    url = f"{base_url}/TableBundles/{file_name}"
                elif args.type == "Media":
                    sub = "MediaResources-Windows" if args.client == "Windows" else "MediaResources"
                    url = f"{base_url}/{sub}/{file_name}"
                else:
                    url = f"{base_url}/{args.client}_PatchPack/{file_name}"
                download_list.append((url, os.path.join("Download_Temp", file_name)))

        elif Config.server == "CN":
            catalog_file = "TableCatalog.json" if args.type == "Table" else "MediaCatalog.json"
            with open(os.path.join("Download", catalog_file), "r", encoding="utf-8") as f:
                catalog_data = json.load(f)

            for file_name in args.files:
                if args.type == "Table":
                    info = catalog_data.get("Table", {}).get(file_name)
                    val = str(info.get("Crc")) if info else None
                    url = f"{base_url}/pool/TableBundles/{val[:2]}/{val}" if val else None
                elif args.type == "Media":
                    info = catalog_data.get(file_name.lower())
                    val = str(info.get("Hash")) if info else None
                    url = f"{base_url}/pool/MediaResources/{val[:2]}/{val}" if val else None
                else:
                    url = f"{base_url}/AssetBundles/{args.client}/{file_name}"

                if url:
                    download_list.append((url, os.path.join("Download_Temp", file_name)))

        elif Config.server == "GL":
            for file_name in args.files:
                if args.type == "Table":
                    url = f"{base_url}/Preload/TableBundles/{file_name}"
                elif args.type == "Media":
                    url = ""  # Placeholder for Media
                else:
                    url = ""  # Placeholder for Bundle
                
                if url:
                    download_list.append((url, os.path.join("Download_Temp", file_name)))

    for url, path in download_list:
        if FileDownloader(url, enable_progress=True).save_file(path):
            print(f"成功: {path}")
