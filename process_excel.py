import os
from argparse import ArgumentParser
from pathlib import Path
from utils.config import Config
from xtractor.table import TableProcess

def parse_args():
    p = ArgumentParser(description="JSON 数据提取/打包工具")
    p.add_argument("table_file_folder", type=Path, help="ExcelDB.db和Excel.zip的路径")
    p.add_argument("file_path", type=Path, help="文件的输出路径/需打包的文件输入路径")
    p.add_argument("server", type=str, choices=["CN", "GL", "JP"], help="服务器区域，用于自适应加解密方式")
    p.add_argument("type", type=str, choices=["Extract", "Repack"], help="选择加密/解密文件")
    p.add_argument("--db_key", type=str, help="加解密数据库所需的密钥 (如果有则使用，无则正常)")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()

    args.file_path.mkdir(parents=True, exist_ok=True)

    Config.server = args.server

    # 密钥自己搞，由服务器下发，可解析getway或hook获取
    if args.db_key:
        Config.db_password = args.db_key

    process = TableProcess(str(args.table_file_folder), str(args.file_path), "FlatData")

    if os.path.exists(os.path.join(args.table_file_folder, "ExcelDB.db")):
        process.process_table("ExcelDB.db", args.type)
    if os.path.exists(os.path.join(args.table_file_folder, "Excel.zip")):
        process.process_table("Excel.zip", args.type)
