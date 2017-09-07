from setuptools import (setup,
                        find_packages)

from collector.config import PACKAGE_NAME

setup(name=PACKAGE_NAME,
      packages=find_packages(),
      version='0.0.0',
      author='Azat Ibrakov',
      author_email='azatibrakov@gmail.com',
      install_requires=[
          'aiohttp>=2.2.5',  # asynchronous HTTP
          'pymongo>=3.5.1',
      ])
