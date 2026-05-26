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
    
    res_backup_path = base_dir / "ResBackup"
    res_backup_path.mkdir(exist_ok=True)

    apk_tools = ApkTools()
    apk_url, version = Server().get_apk_url()
    FileDownloader(url=apk_url, headers={"User-Agent": "Androidkb"}).save_file(str(apk_path))

    # 将三个apk文件解压到Temp/Decoded/assets文件夹下
    ZipUtils.extract_zip(str(apk_path), str(decoded_path / "assets"), keywords=["assets/com.YostarJP.BlueArchive"])
    apks = FileUtils.find_files(str(decoded_path / "assets"), ["UnityDataAssetPack", "config", "BlueArchive"])
    # 获得main apk文件名
    main_apk = next(a for a in apks if "UnityDataAssetPack" not in a and "config" not in a)
    others = [a for a in apks if a != main_apk]

    print(f"[DEBUG] 确定 Main APK: {main_apk}")

    # 备份dex文件
    with zipfile.ZipFile(main_apk, 'r') as z:
        dex_files = [f for f in z.namelist() if f.startswith("classes") and f.endswith(".dex")]
        for dex in dex_files:
            with open(dex_backup_path / dex, 'wb') as f:
                f.write(z.read(dex))
            print(f"[DEBUG] 已备份 Main APK DEX: {dex}")
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

    # 备份logo视频文件
    target_res_file = "assets/bin/Data/sharedassets0.resource"
    src_res_path = main_output_path / target_res_file
    if src_res_path.exists():
        dst_res_path = res_backup_path / target_res_file
        dst_res_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_res_path, dst_res_path)
        print(f"[DEBUG] 已备份原版资源: {target_res_file}")

    # 备份Video视频文件夹
    target_video_dir = "assets/Video"
    src_video_path = main_output_path / target_video_dir
    if src_video_path.exists():
        dst_video_path = res_backup_path / target_video_dir
        dst_video_path.parent.mkdir(parents=True, exist_ok=True)
        copy_tree(str(src_video_path), str(dst_video_path))
        print(f"[DEBUG] 已备份原版视频文件夹: {target_video_dir}")

    apk_tools.modify_manifest(main_output_path, is_coexist=True)

    # 封包
    apk_tools.build(main_output_path, "蔚蓝档案.apk")
    
    rebuilt_apk = Path("蔚蓝档案.apk")
    temp_apk = rebuilt_apk.with_suffix(".tmp.apk")
    no_compress = ["resources.arsc", "assets/bin/Data/sharedassets0.resource", "assets/Video/"]

    with zipfile.ZipFile(rebuilt_apk, 'r') as zin, zipfile.ZipFile(temp_apk, 'w') as zout:
        for item in zin.infolist():
            if item.filename.startswith("classes") and item.filename.endswith(".dex"):
                continue
            if item.filename.startswith(tuple(no_compress)):
                if "resources.arsc" not in item.filename:
                    continue
            
            new_item = zipfile.ZipInfo(item.filename)
            new_item.date_time = item.date_time
            new_item.external_attr = item.external_attr
            
            if item.filename == "resources.arsc":
                new_item.compress_type = zipfile.ZIP_STORED
            else:
                new_item.compress_type = zipfile.ZIP_DEFLATED
                
            zout.writestr(new_item, zin.read(item.filename))
    
        for root, dirs, files in os.walk(res_backup_path):
            for file in files:
                full_path = Path(root) / file
                rel_path = full_path.relative_to(res_backup_path)
                arcname = str(rel_path).replace(os.path.sep, '/')
                
                new_item = zipfile.ZipInfo(arcname)
                new_item.compress_type = zipfile.ZIP_STORED
                with open(full_path, 'rb') as f:
                    zout.writestr(new_item, f.read())
                print(f"[DEBUG] [原文件注入] 成功添加原始不压缩资源 (STORED): {arcname}")

        for dex_file in os.listdir(dex_backup_path):
            dex_path = dex_backup_path / dex_file
            new_item = zipfile.ZipInfo(dex_file)
            new_item.compress_type = zipfile.ZIP_DEFLATED
            with open(dex_path, 'rb') as f:
                zout.writestr(new_item, f.read())
            print(f"[DEBUG] [原文件注入] 成功添加原始 DEX (DEFLATED): {dex_file}")

    rebuilt_apk.unlink()
    apk_tools.sign(temp_apk , rebuilt_apk)
    temp_apk.unlink()

#    shutil.rmtree(dex_backup_path)
#    shutil.rmtree(res_backup_path)
#    shutil.rmtree(main_output_path)
