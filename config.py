import os

class Config:
    USERNAME = os.environ.get('TT_USER')
    PASSWORD = os.environ.get('TT_PASS')
    URL_ROOT = os.environ.get('TT_ROOT')
