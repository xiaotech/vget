import re
import requests
from loguru import logger
from urllib.parse import urlparse
from em3u8 import MClient
from Crypto.Cipher import AES
import shutil
from typing import Optional,Dict,List,Union,Tuple
import tempfile
import os



class EM3U8:
    '''
    m3u8 Class

    init by ulr or content
    '''


    def __init__(self,content:Optional[str] = None,url:Optional[str] = None,timeout:int=10) -> None:
        self.__content = content
        self.url = url
        self.__timeout = timeout
        self.__tss = []
        self.__key = {}

    @property
    def key(self) -> Optional[Dict[str,str]]:
        """
        get m3u8 key info

        :return: key info
        """
        if not self.__key:
            key_pattern = re.compile(r'#EXT-X-KEY:([^\n]+)\n')
            if not self.__content:
                self.__content = self.__get_content_from_url()
            keys = key_pattern.findall(self.__content)
            if keys:
                self.__key = dict(re.findall(r'([^=,]+)=([^,]+)', keys[0]))
            else:
                self.__key = {}
        return self.__key

    @property
    def content(self) -> Optional[str]:
        if not self.__content:
            self.__content = self.__get_content_from_url()
        return self.__content

    @property
    def tss(self) -> Optional[List[str]]:
        '''
        get tss url from content
        :return: tss addr url
        '''
        if self.__tss:
            return self.__tss
        if not self.__content:
            if not self.url:
                self.__tss = []
            else:
                self.__content = self.__get_content_from_url()
        self.__tss = self.__get_tss_from_content()
        return self.__tss
        

    def __get_tss_from_content(self) -> list[str]:
        if not self.__content:
            return []
        ts_pattern = re.compile(r'#EXTINF:[0-9.]+,\n([^\n]+)\n')
        data = ts_pattern.findall(self.__content)
        return [self.__get_absolute_url(ts_url) for ts_url in data]
            
    def __get_content_from_url(self) -> str:
        url = self.url
        while True:
            logger.debug(f"req: {url}")
            res = requests.get(url,verify=False,timeout=self.__timeout)
            if res.status_code == 302:
                url = res.headers["location"]                
                logger.debug(f"302 -> {url}")
                continue
            elif res.status_code == 200:
                result,data = self.__valid_final_m3u8(res.text)
                if len(res.text) > 400:
                    logger.debug(res.text[:200] + "\n...\n" + res.text[-200:])
                else:
                    logger.debug(res.text)
                if result:                    
                    break
                else:
                    url = data                   
                    logger.debug(f"sub - > {url}")
            else:
                logger.error(f"status code: {res.status_code}")
                logger.error(res.text)
                break
        self.url = url
        self.__content = res.text       
        return self.__content

    def __valid_final_m3u8(self,data:str) -> Tuple[bool,Optional[str]]:
        if "#EXTINF" in data:
            return True,None
        else:
            for line in data.split("\n"):
                if not line.startswith("#"):
                    new_url = line
                    break
            return False,self.__get_absolute_url(new_url)

    def __get_baseurl(self,ts_url:str) -> str:
        if not self.url or ts_url.startswith("http"):
            return ""
        elif ts_url.startswith("/"):
            urlp = urlparse(self.url)
            return urlp.scheme + "://" + urlp.netloc
        else:
            return self.url[0:self.url.rfind("/")+1]
    
    def __get_absolute_url(self,url:str) -> str:
        url = url.replace('"','')
        return self.__get_baseurl(url) + url

    def download_vedio(self,save_path:Optional[str]=None,workers:int=1,thread:bool=True,debug:bool=False):
        """
        download vedio

        :param save_path: vedio save path
        :param workers: thread or process counts
        :param thread: use thread or process model
        :param debug: show debug msg
        """
        if os.path.exists(save_path):
            choice = input(f"【{save_path}】文件已存在，是否重新下载  (Y/N)?")
            if not choice.lower() == "y":
                exit(1)
            try:
                os.remove(save_path)
            except Exception as e:
                logger.error(e)
                exit(1)

        save_path = MClient(self.tss).download_vedio(save_path,workers,thread,debug=debug)
        if self.key.get("URI",None):
            self.dencrypt(save_path)

    def dencrypt(self,vedio_path:str,key:Optional[str]=None,iv=b"\x00"*16):
        """
        dencrypt vedio 

        :param vedio_path: vedio path
        :param key: encrypt key 
        :param iv: encrypt iv 
        """
        if not key:
            key = self.key.get("URI",None)
            key = self.__get_absolute_url(key)
        
        if self.key.get("IV",None):
            iv = self.key.get("IV")
        
        logger.debug(f"start dencrypting...")
        key = requests.get(key,verify=False).content
        logger.debug(f"dencrypt: key -> {key},iv -> {iv}")
        cipher = AES.new(key,AES.MODE_CBC,iv)
        with tempfile.TemporaryFile() as temp_file:
            with open(vedio_path,"rb") as rr:    
                temp_file.write(cipher.decrypt(rr.read()))
            temp_file.seek(0)
            with open(vedio_path,"wb") as ww:
                ww.write(temp_file.read())            
        logger.debug("dencrypt done")
        
        
