from bs4 import BeautifulSoup
import requests
import re
from typing import Optional
from urllib.parse import urlparse
import os



class Site():
    name = "SITE"
    
    def __init__(self,url,timeout=10):
        self.url = url
        self._text = None
        self._title = None
        self.err = None
        self._m3u8_filter = [
            r'(http[^"]+m3u8)',
            r'"([^",]+m3u8[^"]{0,})"',
        ]
        self._title_filter = r'(^[^_]+_[^_]+)_'
        self.__timeout = timeout
                
    @property
    def m3u8(self)->Optional[str]:
        """
        get m3u8 content

        :return: m3u8 text
        """
        urls = []
        if not self._text:
            self._text = requests.get(self.url,verify=False,timeout=self.__timeout).text
        soup = BeautifulSoup(self._text,"html.parser")
        scripts = soup.find_all("script")
        
        for script in scripts:
            for filter in self._m3u8_filter:
                  
                m_urls = re.compile(filter).findall(str(script))      
                if m_urls:                
                    urls.extend(m_urls)
                    break        
        if urls:
            return [self.__format_url(url) for url in urls]
        else:
            self.err = "Site: No resource (only support small sites,if you really want,connect to xiaotech@163.com)"
            return None

    def __format_url(self,url:str) -> str:
        url = url.replace("\\","")
        if url.startswith("http"):
            return url
        elif url.startswith("/"):
            urlp = urlparse(self.url)
            return urlp.scheme + "://" + urlp.netloc + url
        else:
            return os.path.dirname(self.url) + url

    @property
    def title(self) -> str:
        """
        get title

        :return: titie
        """
        if not self._title:
            if not self._text:
                self._text = requests.get(self.url,verify=False,timeout=20).text
            soup = BeautifulSoup(self._text,"html.parser")
            title = re.compile(self._title_filter).findall(soup.title.string)
            if title:
                self._title = title[0]
            else:
                self._title = soup.title.string
        return self._title
