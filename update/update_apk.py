import shutil
import os
import zipfile
from pathlib import Path
from utils.config import Config
from utils.regions import Server
from utils.apktools import ApkTools
from lib.downloader import FileDownloader
from utils.util import ZipUtils, FileUtils
from distutils.dir_util import copy_tree

if __name__ == "__main__":
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
    # 确保mp4视频不会被压缩
    if 'doNotCompress:' in yml_content and '- mp4' not in yml_content:
        yml_content = yml_content.replace('doNotCompress:', 'doNotCompress:\n- mp4')
        with open(yml_path, 'w', encoding='utf-8') as f:
            f.write(yml_content)

    apk_tools.modify_manifest(main_output_path, True)
    apk_tools.modify_resources(main_output_path)

    # 封包
    apk_tools.build(main_output_path, "蔚蓝档案.apk")
    
    rebuilt_apk = Path("蔚蓝档案.apk")
    temp_apk = rebuilt_apk.with_suffix(".tmp.apk")

    TARGET_DATE = (1981, 1, 1, 0, 0, 0)

    with zipfile.ZipFile(rebuilt_apk, 'r') as zin, zipfile.ZipFile(temp_apk, 'w') as zout:
        for item in zin.infolist():
            if item.filename.startswith("classes") and item.filename.endswith(".dex"):
                continue
            
            new_item = zipfile.ZipInfo(item.filename)
            new_item.date_time = TARGET_DATE  # 修改非DEX文件的日期
            new_item.external_attr = item.external_attr
            
            # resources.arsc以非压缩方式存储
            if item.filename == "resources.arsc":
                new_item.compress_type = zipfile.ZIP_STORED
            else:
                new_item.compress_type = item.compress_type
                
            zout.writestr(new_item, zin.read(item.filename))
    
        for dex_file in os.listdir(dex_backup_path):
            dex_path = dex_backup_path / dex_file
            new_item = zipfile.ZipInfo(dex_file)
            new_item.date_time = TARGET_DATE
            new_item.compress_type = zipfile.ZIP_DEFLATED
            with open(dex_path, 'rb') as f:
                zout.writestr(new_item, f.read())
            print(f"成功添加原始 DEX并修改时间: {dex_file}")

    rebuilt_apk.unlink()
    apk_tools.sign(temp_apk, rebuilt_apk)
    temp_apk.unlink()

    shutil.rmtree(dex_backup_path)
    shutil.rmtree(main_output_path)
