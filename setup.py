from setuptools import setup, find_packages

__licence__ = 'GPLv3'
__author__ = 'Nabil-Fareed Alikhan'
__author_email__ = 'nabil@happykhan.com'
__version__ = "1.0.1"


setup(
    name='subhelper',
    version=__version__,
    license=__licence__,
    author=__author__,
    author_email=__author_email__,
    packages=find_packages('subhelper'),
    package_dir={'': 'src'},
    url='https://github.com/happykhan/subhelper',
    keywords='gisaid',
    install_requires=[
          'biopython',
      ],

)