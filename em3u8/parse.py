from urllib.parse import urlparse
from em3u8.sites import *
import random
import string
from typing import Optional,Dict



class Parse():
    '''
    parse site 
    '''
    def __init__(self,url:str):
        self.__m3u8 = None
        self.__url:str = url
        self.__title = None
        self.__sites = {
            "yunbtv.net": YunBTV,
        }
        self.__parser = None
        self.err = None
        

    @property
    def title(self) -> str:
        try:
            if not self.__title:
                self.__title = self.parser.title
        except Exception as e:
            self.err = e
            self.__title = e
        return self.__title
    
    @property
    def parser(self) -> Site:
        if not self.__parser:
            # parser_class = self.__sites.get(self.host,Site)
            parser_class = self.__get_parser_class(self.host)
            self.__parser = parser_class(self.__url)
        return self.__parser
    
    def __get_parser_class(self,host:str) -> Site:
        for site in self.__sites:
            if site in host:
                return self.__sites[site]
        return Site

    @property
    def m3u8(self) -> Optional[str]:
        try:
            if not self.__m3u8:
                if self.__url.endswith(".m3u8"):
                    self.__m3u8 = self.__url
                    self.__title = f"m3u8_{''.join(random.choices(string.ascii_letters+string.digits,k=10))}"
                else:
                    self.__m3u8 = self.parser.m3u8
                    self.err = self.parser.err
        except Exception as e:
            self.err = e
            self.__m3u8 = None
        
        return self.__m3u8

    @property
    def sites(self) -> Dict[str,Site]:
        return self.__sites

    @property
    def host(self) -> str:
        urlp = urlparse(self.__url)
        return urlp.netloc
            