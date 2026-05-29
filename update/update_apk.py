import shutil
import os
import zipfile
import argparse
import base64
import json
from pathlib import Path
from utils.config import Config
from utils.regions import Server
from utils.apktools import ApkTools
from lib.downloader import FileDownloader
from utils.util import ZipUtils, FileUtils, CommandUtils
from distutils.dir_util import copy_tree
from xtractor.bundle import BundleExtractor
from lib.encryption import create_key, convert_string, encrypt_string, xor

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update Blue Archive APK")
    parser.add_argument("--sdkurl", type=str, help="修改SDK_Url的值")
    parser.add_argument("--gamemainconfig", type=str, help="修改GameMainConfig的字段")
    args = parser.parse_args()

    Config.server = "JP"
    base_dir = Path("Temp")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    decoded_path = base_dir / "Decoded"
    temp_extract_path = base_dir / "TempExtract"
    main_output_path = base_dir / "MainOutput"
    apk_path = base_dir / f"Temp_{Config.server}.apk"
    
    dex_backup_path = base_dir / "DexBackup"
    dex_backup_path.mkdir(exist_ok=True)

    apk_tools = ApkTools()
    apk_url, version = Server().get_apk_url()
    FileDownloader(url=apk_url, headers={"User-Agent": "Androidkb"}).save_file(str(apk_path))

    # 将三个apk文件解压到Temp/Decoded/assets文件夹下
    ZipUtils.extract_zip(str(apk_path), str(decoded_path / "assets"), keywords=["assets/com.YostarJP.BlueArchive"])
    apks = FileUtils.find_files(str(decoded_path / "assets"), ["UnityDataAssetPack", "config", "BlueArchive"])
    # 获得main apk文件名
    main_apk = next(a for a in apks if "UnityDataAssetPack" not in a and "config" not in a)
    others = [a for a in apks if a != main_apk]

    print(f"确定 Main APK: {main_apk}")

    # 备份dex文件
    with zipfile.ZipFile(main_apk, 'r') as z:
        dex_files = [f for f in z.namelist() if f.startswith("classes") and f.endswith(".dex")]
        for dex in dex_files:
            with open(dex_backup_path / dex, 'wb') as f:
                f.write(z.read(dex))
            print(f"已备份 Main APK DEX: {dex}")

    # 对main apk拆包
    apk_tools.extract(main_apk, main_output_path)
    # 把其他两个apk的assets和lib文件夹扔到Temp/TempExtract文件夹下
    ZipUtils.extract_zip(others, str(temp_extract_path))
    for folder in ["lib", "assets"]:
        src = temp_extract_path / folder
        if src.exists(): 
            copy_tree(str(src), str(main_output_path / folder))

    shutil.rmtree(decoded_path)
    shutil.rmtree(temp_extract_path)
    apk_path.unlink()

    yml_path = main_output_path / "apktool.yml"
    with open(yml_path, 'r', encoding='utf-8') as f:
        yml_content = f.read()
        
    # 确保 mp4 视频和 arsc 文件都不会被压缩
    need_write = False
    if 'doNotCompress:' in yml_content:
        if '- mp4' not in yml_content:
            yml_content = yml_content.replace('doNotCompress:', 'doNotCompress:\n- mp4')
            with open(yml_path, 'w', encoding='utf-8') as f:
                f.write(yml_content)

    apk_tools.modify_manifest(main_output_path, True)
    apk_tools.modify_resources(main_output_path)

    replace_dir = Path("BAJpApkSrc/Replace")
    if replace_dir.exists():
        copy_tree(str(replace_dir), str(main_output_path / "assets"))

    modified_dir = Path("BAJpApkSrc/Modified")
    # 修改 SDK URL
    if args.sdkurl:
        sdk_config_path = main_output_path / "assets" / "SDKConfigSettings.json"
        with open(sdk_config_path, "r", encoding="utf-8") as f:
            sdk_config = json.load(f)
            old_url = sdk_config["Regions"]["Jp"].get("Sdk_Url")
            sdk_config["Regions"]["Jp"]["Sdk_Url"] = args.sdkurl
            print(f"SDK URL 已成功修改: {old_url} -> {args.sdkurl}")

        with open(sdk_config_path, "w", encoding="utf-8") as f:
            json.dump(sdk_config, f, indent=4, ensure_ascii=False)

    # 修改 GameMainConfig
    if args.gamemainconfig:
        print("[*] 正在读取并修改 GameMainConfig...")
        data_folder = str(main_output_path / "assets" / "bin" / "Data")
        extractor = BundleExtractor()
        url_objs = extractor.search_unity_pack(
            data_folder, 
            data_type=["TextAsset"], 
            data_name=["GameMainConfig"], 
            condition_connect=True
        )

        if url_objs:
            raw_script = url_objs[0].read().m_Script
            
            # 兼容处理
            if isinstance(raw_script, str):
                raw_script = raw_script.encode("utf-8", "surrogateescape")
            # raw bytes -> base64 -> convert_string(包含b64解密+XOR+utf16解码)
            b64_data = base64.b64encode(raw_script).decode("utf-8")
            json_str = convert_string(b64_data, create_key("GameMainConfig"))
            try:
                raw_json_obj = json.loads(json_str)
                ciphers = {
                    "ServerInfoDataUrl": "X04YXBFqd3ZpTg9cKmpvdmpOElwnamB2eE4cXDZqc3ZgTg==",
                    "DefaultConnectionGroup": "tSrfb7xhQRKEKtZvrmFjEp4q1G+0YUUSkirOb7NhTxKfKv1vqGFPEoQqym8=",
                    "SkipTutorial": "8AOaQvLC5wj3A4RC78L4CNEDmEL6wvsI",
                    "Language": "wL4EWsDv8QX5vgRaye/zBQ==",
                }
                gmc_dict = json.loads(args.gamemainconfig)

                # 覆盖并重新加密字段内部的值
                for key, val in gmc_dict.items():
                    if key in ciphers:
                        cipher_key = ciphers[key]
                        raw_json_obj[cipher_key] = encrypt_string(val, create_key(key))
                        print(f"[*] GameMainConfig 字段已更新: {key} = {val}")
                    else:
                        print(f"[-] 警告: 未知的 GameMainConfig 字段 '{key}'，跳过。")
                # 重新打包整个JSON
                new_json_str = json.dumps(raw_json_obj, separators=(',', ':'))
                
                # 外层的 TextAsset 文件不是 Base64，逆向还原为 utf-16le + xor 的纯字节流(bytes)
                new_raw_script = xor(new_json_str.encode("utf-16le"), create_key("GameMainConfig"))
                
                # 写入到 Modified 文件夹
                modified_dir.mkdir(parents=True, exist_ok=True)
                with open(modified_dir / "GameMainConfig", "wb") as f:
                    f.write(new_raw_script)
                print("[*] GameMainConfig 加密修改完毕，已保存。")
                
            except json.JSONDecodeError:
                print("[-] 错误: GameMainConfig 解密或解析为JSON时失败。")
        else:
            print("[-] 错误: 在目标资源包中未搜索到 GameMainConfig TextAsset。")

    if modified_dir.exists():
        extractor = BundleExtractor()
        data_folder = str(main_output_path / "assets" / "bin" / "Data")
        for root, _, files in os.walk(modified_dir):
            for file_name in files:
                file_path = Path(root) / file_name
                asset_name = file_path.stem
                print(f"[*] 正在将修改文件写入替换 Bundle 资源: {file_name} -> (Asset: {asset_name})")
                extractor.replace_asset_from_file(data_folder, asset_name, str(file_path), crc_fix=True)

    # 封包为未对齐的临时 APK
    raw_apk = Path("unaligned.apk")
    temp_align = Path("temp.apk")
    final_apk = Path("蔚蓝档案.apk")

    apk_tools.build(main_output_path, str(raw_apk))
    
    # 还原 DEX 并清理时间戳 (输出到 temp_align)
    TARGET_DATE = (1981, 1, 1, 0, 0, 0)
    with zipfile.ZipFile(raw_apk, 'r') as zin, zipfile.ZipFile(temp_align, 'w') as zout:
        for item in zin.infolist():
            if item.filename.startswith("classes") and item.filename.endswith(".dex"):
                continue
            new_item = zipfile.ZipInfo(item.filename)
            new_item.date_time = TARGET_DATE
            new_item.external_attr = item.external_attr
            new_item.compress_type = item.compress_type
            zout.writestr(new_item, zin.read(item.filename))
    
        for dex_file in os.listdir(dex_backup_path):
            with open(dex_backup_path / dex_file, 'rb') as f:
                new_item = zipfile.ZipInfo(dex_file)
                new_item.date_time = TARGET_DATE
                new_item.compress_type = zipfile.ZIP_DEFLATED
                zout.writestr(new_item, f.read())
    raw_apk.unlink()
    
    print("正在进行 Zipalign 4字节对齐...")
    success, err = CommandUtils.run_command("zipalign", "-p", "-f", "4", str(temp_align), str(final_apk))
    
    if success:
        print("对齐完成。")
        temp_align.unlink()
    else:
        print(f"对齐错误: {err}")

    print("开始进行 APK 签名...")
    apk_tools.sign(str(final_apk), str(final_apk))

    shutil.rmtree(dex_backup_path)
    shutil.rmtree(main_output_path)
