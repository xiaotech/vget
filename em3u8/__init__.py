import warnings
from urllib3.exceptions import InsecureRequestWarning
from em3u8.httpclient import MClient
from em3u8.m3u8 import EM3U8
from em3u8.parse import Parse
from em3u8.logger import Log

warnings.simplefilter('ignore', InsecureRequestWarning)
version = "0.4.1"
author = "xiaojun"
author_email = "xiaotech@163.com"
web_url = "https://github.com/xiaotech/vget"
release_name = "vget"