import shutil
import json
import re
import os
import zipfile
import base64
from pathlib import Path
from lxml import etree
from utils.util import CommandUtils, ZipUtils, FileUtils
from utils.config import Config
from utils.regions import Server
from lib.downloader import FileDownloader
from distutils.dir_util import copy_tree
from xtractor.bundle import BundleExtractor
from lib.encryption import create_key, convert_string, encrypt_string, xor

class ApkTools:
    def _run_apktool(self, args):
        success, error = CommandUtils.run_command("java", "-jar", "BAJpApkSrc/apktool.jar", *args)
        if not success:
            raise Exception(f"apktool failed: {error}")
        return success

    def extract(self, apk_path, output_dir):
        out_path = Path(output_dir)
        if out_path.exists():
            shutil.rmtree(out_path)
        return self._run_apktool(["d", "-f", str(apk_path), "-o", str(out_path)])

    def build(self, input_dir, output_apk):
        args = ["b", str(input_dir), "-o", str(output_apk)]
        return self._run_apktool(args)

    def modify_manifest(self, output_dir, is_coexist=False, trust_cert=False):
        manifest_path = Path(output_dir) / "AndroidManifest.xml"
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if is_coexist:
            host_matches = list(re.finditer(r'(android:host=")([^"]+)(")', content))
            host_values = [match.group(2) for match in host_matches]

            for i, match in enumerate(host_matches):
                temp_marker = f"__HOST_TEMP_{i}__"
                content = content.replace(match.group(0), f'{match.group(1)}{temp_marker}{match.group(3)}')
            
            content = content.replace('com.YostarJP.BlueArchive', 'com.BCJP.BlueArchive')
            # 共存需要修这些，添加包名前缀，否则闪退
            patterns_to_prefix = [
                'com.google.android.gms.permission.AD_ID',
                'com.facebook.katana.provider.PlatformProvider',
                'com.google.android.finsky.permission.BIND_GET_INSTALL_REFERRER_SERVICE',
                'com.google.android.c2dm.permission.RECEIVE',
                'android.permission.CHANGE_NETWORK_STATE',
                'android.permission.WRITE_SETTINGS'
            ]    

            for pattern in patterns_to_prefix:
                content = content.replace(pattern, f'com.BCJP.BlueArchive_{pattern}')

            for i, original_host in enumerate(host_values):
                temp_marker = f"__HOST_TEMP_{i}__"
                content = content.replace(temp_marker, original_host)

        root = etree.fromstring(content.encode('utf-8'))

        if trust_cert:
            app_element = root.find(".//application")
            if app_element is not None:
                app_element.set('{http://schemas.android.com/apk/res/android}networkSecurityConfig', '@xml/network_security_config')

        # 删除Split标识
        for attr in ['{http://schemas.android.com/apk/res/android}requiredSplitTypes', '{http://schemas.android.com/apk/res/android}splitTypes']:
            if attr in root.attrib: 
                del root.attrib[attr]

        # 合并资源        
        ns = {'android': 'http://schemas.android.com/apk/res/android'}
        for meta in root.findall(".//meta-data", namespaces=ns):
            name = meta.get('{http://schemas.android.com/apk/res/android}name')
            if name == "com.android.vending.splits.required":
                meta.set('{http://schemas.android.com/apk/res/android}name', 'com.android.dynamic.apk.fused.modules')
                meta.set('{http://schemas.android.com/apk/res/android}value', 'UnityDataAssetPack,base')
        
        new_xml = etree.tostring(root, encoding='utf-8', pretty_print=True).decode('utf-8')
        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write(new_xml)

    def modify_resources(self, output_dir):
        base_path = Path(output_dir)
    
        # 修改 app_name
        for p in base_path.glob("res/values*/strings.xml"):
            try:
                content = p.read_text(encoding='utf-8')
                if '<string name="app_name">ブルアカ</string>' in content:
                    p.write_text(content.replace('<string name="app_name">ブルアカ</string>', '<string name="app_name">蔚蓝档案</string>'), encoding='utf-8')
            except Exception as e:
                print(f"Failed to modify strings.xml at {p}: {e}")

        # 修改登录界面文本
        try:
            res_data = json.loads(Path("BAJpApkSrc/resources.json").read_text(encoding='utf-8'))
            ja_path = base_path / "res/values-ja/strings.xml"

            content = ja_path.read_text(encoding='utf-8')
            for item in res_data:
                content = re.sub(rf'(?s)<string name="{item["name"]}">.*?</string>', f'<string name="{item["name"]}">{item["text"]}</string>', content)
            ja_path.write_text(content, encoding='utf-8')
        except Exception as e:
            print(f"Failed to process values-ja/strings.xml or resources.json: {e}")

    def sign(self, apk_path, out_path):
        success, error = CommandUtils.run_command('java', '-jar', "BAJpApkSrc/apksigner.jar", 'sign', '--ks', "BAJpApkSrc/beichen.jks", '--ks-pass', 'pass:北辰汉化组a', '--key-pass', 'pass:北辰汉化组a', '--out', out_path, '--v1-signing-enabled', 'true', '--v2-signing-enabled', 'true', '--v3-signing-enabled', 'true', apk_path)
        if not success:
            raise Exception(f"apktool failed: {error}")
        return success

    def modify_sdk_url(self, main_output_path, sdkurl):
        sdk_config_path = main_output_path / "assets" / "SDKConfigSettings.json"
        with open(sdk_config_path, "r", encoding="utf-8") as f:
            sdk_config = json.load(f)
            old_url = sdk_config["Regions"]["Jp"].get("Sdk_Url")
            sdk_config["Regions"]["Jp"]["Sdk_Url"] = sdkurl
            print(f"SDK URL 已成功修改: {old_url} -> {sdkurl}")

        with open(sdk_config_path, "w", encoding="utf-8") as f:
            json.dump(sdk_config, f, indent=4, ensure_ascii=False)

    def modify_game_main_config(self, main_output_path, gamemainconfig, modified_dir):
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
                gmc_dict = json.loads(gamemainconfig)

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

    def apply_bundle_modifications(self, main_output_path, modified_dir):
        if modified_dir.exists():
            extractor = BundleExtractor()
            data_folder = str(main_output_path / "assets" / "bin" / "Data")
            for root, _, files in os.walk(modified_dir):
                for file_name in files:
                    file_path = Path(root) / file_name
                    asset_name = file_path.stem
                    print(f"[*] 正在将修改文件写入替换 Bundle 资源: {file_name} -> (Asset: {asset_name})")
                    extractor.replace_asset_from_file(data_folder, asset_name, str(file_path), crc_fix=True)

    def modify_geetest_lang(self, output_dir):
        gt4_path = Path(output_dir) / "assets" / "gt4.js"
        if gt4_path.exists():
            content = gt4_path.read_text(encoding='utf-8')
            old_str = "lang: config.language? config.language : navigator.appName === 'Netscape' ? navigator.language.toLowerCase() : navigator.userLanguage.toLowerCase()"
            if old_str in content:
                content = content.replace(old_str, "lang: 'zho'")
                gt4_path.write_text(content, encoding='utf-8')

    def main(self, coexist=False, sdkurl=None, gamemainconfig=None, trustcert=False, modifylogin=False):
        Config.server = "JP"
        base_dir = Path("Temp")
        base_dir.mkdir(parents=True, exist_ok=True)
        
        decoded_path = base_dir / "Decoded"
        temp_extract_path = base_dir / "TempExtract"
        main_output_path = base_dir / "MainOutput"
        apk_path = base_dir / f"Temp_{Config.server}.apk"
        
        dex_backup_path = base_dir / "DexBackup"
        dex_backup_path.mkdir(exist_ok=True)

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
        self.extract(main_apk, main_output_path)
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

        self.modify_manifest(main_output_path, coexist, trustcert)
        
        if trustcert:
            xml_dir = main_output_path / "res" / "xml"
            shutil.copy("BAJpApkSrc/network_security_config.xml", str(xml_dir / "network_security_config.xml"))

        self.modify_resources(main_output_path)

        if modifylogin:
            self.modify_geetest_lang(main_output_path)

        replace_dir = Path("BAJpApkSrc/Replace")
        if replace_dir.exists():
            copy_tree(str(replace_dir), str(main_output_path / "assets"))

        modified_dir = Path("BAJpApkSrc/Modified")
        # 修改 SDK URL
        if sdkurl:
            self.modify_sdk_url(main_output_path, sdkurl)

        # 修改 GameMainConfig
        if gamemainconfig:
            self.modify_game_main_config(main_output_path, gamemainconfig, modified_dir)

        self.apply_bundle_modifications(main_output_path, modified_dir)

        # 封包为未对齐的临时 APK
        raw_apk = Path("unaligned.apk")
        temp_align = Path("temp.apk")
        final_apk = Path("蔚蓝档案.apk")

        self.build(main_output_path, str(raw_apk))
        
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
        self.sign(str(final_apk), str(final_apk))

        shutil.rmtree(dex_backup_path)
        shutil.rmtree(main_output_path)
