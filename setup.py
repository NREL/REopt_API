import os


def gen_data_files(*dirs):
    results = []

    for src_dir in dirs:
        for root, dirs, files in os.walk(src_dir):
            results.append((root, map(lambda f:root + "/" + f, files)))
    return results

# Modify the data install dir to match the source install dir:
from distutils.command.install import INSTALL_SCHEMES

for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages
setup(
  name="reopt_api",
  version="1.0",
  packages=find_packages(),
  author="Nick DiOrio",
  author_email="nicholas.diorio@nrel.gov",
  description="REopt API",
  include_package_data=True,
  data_files=gen_data_files("Xpress")
)


