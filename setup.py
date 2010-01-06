from setuptools import setup, find_packages

setup(name='django-slimmer',
version='0.0.1',
description='Html compression as middleware and view decorators',
author='Harley Bussell',
author_email='modmac@gmail.com',
url='http://github.com/hbussell/django-slimmer',
classifiers=[
  "Programming Language :: Python",
  "Development Status :: 4 - Beta",
  "Intended Audience :: Developers",
  "Framework :: Django",
],
keywords='django html compressor',
zip_safe=False,
license='MIT',
install_requires=[
'setuptools',
],
packages = find_packages(),
include_package_data = True,
)
