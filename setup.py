from setuptools import setup,find_packages
from em3u8 import *


setup(
    name=release_name,
    version=version,
    description='A simple tool with m3u8 resouce download package',
    author=author,
    author_email=author_email,
    packages=find_packages(),
    license="Apache 2.0",
    url=web_url,
    install_requires=[
        'loguru',
        'requests',
        'beautifulsoup4',
        'tqdm',
        'pycryptodome',
        'click'
    ],
    entry_points={
        'console_scripts': [
            f'{release_name}=em3u8.cmd:main'
        ]
    }
)
