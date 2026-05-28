import shutil
import json
import re
from pathlib import Path
from utils.util import CommandUtils
from lxml import etree

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

    def modify_manifest(self, output_dir, is_coexist=False):
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
            res_data = json.loads(Path("other/resources.json").read_text(encoding='utf-8'))
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
