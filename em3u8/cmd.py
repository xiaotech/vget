from em3u8 import EM3U8,Parse,Log
from em3u8 import *
from loguru import logger
import click



@click.command
@click.argument("url")
@click.option("--info","-i",help="show resources",is_flag=True)
@click.option("--save-path","-o",help="save vedio path")
@click.option("--workers","-t",help="thread or process counts",default=2,type=int)
@click.option("--process","-p",is_flag=True,help="process model,default thread",default=True)
@click.option("--debug","-d",is_flag=True,help="show debug info")
@click.help_option("--help","-h")
@click.version_option(version=f"{version},{author} <{author_email}>")
def main(url,info,save_path,workers,process,debug):
    
    Log(debug)
    
    site = Parse(url)

    if site.m3u8:
        logger.info(f"名称: {site.title}")
        logger.info(f"资源: {site.m3u8}")
        
        if not info:        
            if not save_path:
                save_path = f"{site.title}.mp4"
            EM3U8(url=site.m3u8[0]).download_vedio(save_path,workers=workers,thread=process,debug=debug)
    else:
        logger.error(f"{site.err}")


if __name__ == "__main__":
    main()