from setuptools import setup, find_packages
import os

setup(name='django-slimmer',
version='0.0.1',
description='Html compression as middleware and view decorators',
author='Harley Bussell',
author_email='modmac@gmail.com',
zip_safe=False,
install_requires=[
'setuptools',
],
packages = find_packages(),
include_package_data = True,
)

