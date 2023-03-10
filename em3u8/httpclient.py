import requests
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor,wait,ALL_COMPLETED
from tqdm import tqdm
import os
from loguru import logger
import tempfile
import random
import string
from typing import Optional,Tuple,List


class MClient():
    '''
    multi processes or threads client Class
    '''
    def __init__(self,urls=[]) -> None:
        self.urls:List[str] = urls

    def __download_file(self,url:str,save_path:str,timeout=10,retry:int=3) -> Tuple[bool,Optional[Exception]]:
        """
        download single file with progressive status

        :param url: file url
        :param save_path: save path
        :param timeout: requests timeout
        :param retry: when failed retry times
        :returns: True or False with error
        """

        count = 0
        while count < retry:
            count += 1
            try:
                response = requests.get(url, stream=True,verify=False,timeout=timeout)
                response.raise_for_status()
                total_size = int(response.headers.get("Content-Length", 0))    
                #init progress bar
                progress = tqdm(
                    response.iter_content(1024), 
                    f"Downloading {self.__get_format_str(os.path.basename(save_path))}", 
                    total=total_size, 
                    unit="B", 
                    unit_scale=True, 
                    unit_divisor=1024
                )
                # wirte data and update progress bar
                with open(save_path, "wb") as f:
                    for data in progress.iterable:
                        f.write(data)
                        progress.update(len(data))
                return (True,None)
            except Exception as e:
                logger.error(f"Times[{count}]: Download {save_path} failed")
                logger.debug(e)
                if count == retry:
                    return (False,e)
                else:
                    continue

    def __get_format_str(self,src:str,length:int=10) -> str:
        if len(src) <= length:
            return src
        else:
            return src[0:length] + "..."

    

    def __init_output(self,save_path:Optional[str]=None) -> str:
        '''
        init save_path env (mkdirs)

        :param save_path: file download path
        :return: save_path (if None default_******.mp4)
        '''
        if not save_path:
            return f"default_{''.join(random.choices(string.ascii_letters + string.digits,k=6))}.mp4"
        out_dir = os.path.dirname(save_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)
        return save_path

    def __download_ts(self,url:str,save_path,pbar:tqdm,timeout=10,retry=3) -> Tuple[bool,Optional[Exception]]:
        '''
        download ts and update pbar

        :param url: ts addr
        :param save_path: ts save path
        :param pbar: update pbar info
        :param timeout: requests timeout
        :param retry: when failed retry times
        :return: True or False with error     
        ''' 
        count = 0
        res = ()
        while count < retry:
            count += 1
            try:
                with open(save_path,"wb") as f:
                    f.write(requests.get(url,verify=False,timeout=timeout).content)
                res = (True,None)
                break
            except Exception as e:
                logger.error(f"Times[{count}]: Download {save_path} failed")
                logger.debug(e)
                if count == retry:
                    res = (False,e)
                    break
                else:
                    continue
            finally:
                pbar.update()
        return res
    
    def __download_vedio_info(self,save_path=None,workers=1,thread=True) -> str:
        '''
        download vedio with multi tss file with info msg

        :param save_path: vedio save path
        :param workers: download thread or process count 
        :param thread: use thread(default) or process model
        :return: vedio save path
        '''
        with tempfile.TemporaryDirectory() as ts_temp_dir:
            save_path = self.__init_output(save_path)
            total = len(self.urls)
            with tqdm(
                desc=f"Downloading {self.__get_format_str(os.path.basename(save_path))}",
                total=total, 
                unit="个", 
                unit_scale=True
            ) as pbar:
                if thread:
                    executor = ThreadPoolExecutor(max_workers=workers)
                else:
                    executor = ProcessPoolExecutor(max_workers=workers)
                tasks = {
                    executor.submit(
                        self.__download_ts,url,
                        f"{ts_temp_dir}/{os.path.basename(url)}",
                        pbar
                    ):f"{ts_temp_dir}/{os.path.basename(url)}" for url in self.urls}
                wait(tasks,return_when=ALL_COMPLETED)
            # merge ts
            with open(save_path,"wb") as ww:
                for ts in tasks.values():
                    if os.path.exists(ts):
                        with open(ts,"rb") as rr:
                            ww.write(rr.read())
            logger.success(f"{os.path.abspath(save_path)} Done!!")
            return save_path

    def download_vedio(self,save_path:Optional[str]=None,workers:int=1,thread:bool=True,debug:bool=False) -> str:
        """
        download vedio and save to save_path

        :param save_path: vedio save path
        :param workers: download thread or process counts
        :param thread: user thread or process
        :param debug: whether show debug info
        :return: downloaded vedio path
        """
        if debug:
            return self.__download_vedio_debug(save_path,workers,thread)
        else:
            return self.__download_vedio_info(save_path,workers,thread)


    def __download_vedio_debug(self,save_path=None,workers=1,thread=True) -> str:
        '''
        download vedio with multi tss file with debug msg

        :param save_path: vedio save path
        :param workers: download thread or process count 
        :param thread: use thread(default) or process model
        :return: vedio save path
        '''
    
        with tempfile.TemporaryDirectory() as ts_temp_dir:
            logger.debug(f"temdir: {ts_temp_dir}")
            save_path = self.__init_output(save_path)      
            if thread:
                executors = ThreadPoolExecutor(max_workers=workers)
            else:
                executors = ProcessPoolExecutor(max_workers=workers)
            logger.debug(f"Start Downloading,total [{len(self.urls)}] ")
            tasks = {
                executors.submit(
                    self.__download_file,url,
                    f"{ts_temp_dir}/{os.path.basename(url)}"
                ):f"{ts_temp_dir}/{os.path.basename(url)}" for url in self.urls
            }
            wait(tasks,return_when=ALL_COMPLETED)
            failed_count = 0
            for task in tasks:
                if not task.result()[0]:
                    failed_count += 1
                    logger.error(f"Failed: {tasks.get(task)}")
            logger.debug(f"Total: {len(tasks)},FAIL: {failed_count},SUC: {len(tasks) - failed_count}")
            #merge ts
            logger.debug("start merge ts")
            with open(save_path,"wb") as ww:
                for ts in tasks.values():
                    if os.path.exists(ts):
                        with open(ts,"rb") as rr:
                            ww.write(rr.read())
            logger.success(f"{os.path.abspath(save_path)} Done!!")
            return save_path
            