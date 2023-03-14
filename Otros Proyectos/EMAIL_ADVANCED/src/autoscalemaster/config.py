import os
from pydantic import BaseSettings

class Config(BaseSettings):
    REDIS_HOST = os.getenv('REDIS_HOST') or ""
    REDIS_PORT = 6379
    REDIS_DB = 0
    LOGTAIL_HOST = ""

config = Config()
