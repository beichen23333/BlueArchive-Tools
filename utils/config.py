from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    threads = 32
    max_threads = threads * 7
    server = "JP"
    proxy = None
    retries = 5
    db_password = ""
