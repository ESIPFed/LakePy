import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

VERSION = '2.2.1'
PACKAGE_NAME = 'lakepy'
AUTHOR = 'James H. Gearon & John D. Franey'
AUTHOR_EMAIL = 'jhgearon@iu.edu'
URL = 'https://github.com/ESIPFed/LakePy'

LICENSE = 'MIT License'
DESCRIPTION = 'Provides access to the Global Lake Level Database and extended functionality for lake water level ' \
              'analysis'
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
    'pymysql',
    'pandas',
    'numpy',
    'matplotlib',
    'seaborn',
    'plotly',
    'datetime',
    'geopandas',
    'shapely',
    'contextily',
    'more-itertools==8.4',
    'tabulate',
    'ipython',
    'leafmap'
]

setup(name = PACKAGE_NAME,
      version = VERSION,
      description = DESCRIPTION,
      long_description = LONG_DESCRIPTION,
      long_description_content_type = LONG_DESC_TYPE,
      author = AUTHOR,
      license = LICENSE,
      author_email = AUTHOR_EMAIL,
      url = URL,
      install_requires = INSTALL_REQUIRES,
      packages = find_packages()
      )
