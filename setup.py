from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages
setup(
  name = "reopt_api",
  version = "1.0",
  packages = find_packages(),
  author = "Nick DiOrio",
  author_email = "nicholas.diorio@nrel.gov",
  description = "REopt API",
  include_package_data = True
)