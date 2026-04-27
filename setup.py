#!/usr/bin/env python
"""The setup script."""
import os
import re

from setuptools import find_packages, setup


def get_version():
    """Get current version from code."""
    regex = r"__version__\s=\s\"(?P<version>[\d\.]+?)\""
    path = ("salus_it600", "__version__.py")
    return re.search(regex, read(*path)).group("version")


def read(*parts):
    """Read file."""
    filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), *parts)
    with open(filename, encoding="utf-8", mode="rt") as fp:
        return fp.read()


with open("README.md") as readme_file:
    readme = readme_file.read()

setup(author="Julius Vitkauskas, Jordi-14",
      author_email="zadintuvas@gmail.com",
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Framework :: AsyncIO",
          "Programming Language :: Python :: 3.7",
          "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator"
      ],
      description="Asynchronous Python client for Salus iT600 devices",
      include_package_data=True,
      install_requires=["aiohttp>=3.8.1", "cryptography>=38.0.1"],
      keywords=["salus", "it600", "api", "async", "client"],
      license="MIT license",
      long_description_content_type="text/markdown",
      long_description=readme,
      name="salus-it600-client",
      packages=find_packages(include=["salus_it600", "salus_it600.*"]),
      url="https://github.com/Jordi-14/salus-it600-client",
      version=get_version(),
      zip_safe=False,
      python_requires='>=3.7',
      )
