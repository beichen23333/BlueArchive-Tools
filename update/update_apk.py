import argparse
from utils.apktools import ApkTools

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update Blue Archive APK")
    parser.add_argument("--sdkurl", type=str, help="修改SDK_Url的值")
    parser.add_argument("--gamemainconfig", type=str, help="修改GameMainConfig的字段")
    parser.add_argument("--coexist", action="store_true")
    parser.add_argument("--trustcert", action="store_true")
    parser.add_argument("--modifylogin", action="store_true")
    args = parser.parse_args()

    apk_tools = ApkTools()
    apk_tools.main(
        coexist=args.coexist,
        sdkurl=args.sdkurl,
        gamemainconfig=args.gamemainconfig,
        trustcert=args.trustcert,
        modifylogin=args.modifylogin
    )
