from argparse import ArgumentParser
from pathlib import Path
from utils.config import Config
from xtractor.table import TableExtractor

def parse_args():
    p = ArgumentParser(description="JSON 数据提取工具")
    p.add_argument("table_file_folder", type=Path, help="ExcelDB.db和Excel.zip的路径")
    p.add_argument("output_path", type=Path, help="提取后JSON文件的输出路径")
    p.add_argument("server", type=str, choices=["CN", "GL", "JP"], help="服务器区域")
    p.add_argument("--db_key", type=str, help="解密数据库所需的密钥 (如果有则解密，无则正常)")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()

    args.output_path.mkdir(parents=True, exist_ok=True)

    Config.server = args.server
    if args.db_key:
        Config.db_password = args.db_key

    extractor = TableExtractor(str(args.table_file_folder), str(args.output_path), "FlatData")

    extractor.extract_table("ExcelDB.db")
    extractor.extract_table("Excel.zip")
