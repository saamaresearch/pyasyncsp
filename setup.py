import setuptools
from setuptools import setup, find_packages

setup(
      name="pyasyncsp",
      packages=find_packages('src', exclude=[]),
      version="0.0.1",
      zip_safe=True,
      include_package_data=True,
      package_dir={'': 'src'}
)