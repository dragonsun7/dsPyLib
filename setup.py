# -*-coding:utf-8-*-
__author__ = 'Dragon Sun'

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dsPyLib",
    version="0.0.1",
    author="Dragon Sun",
    author_email="dragonsun7@163.com",
    description="A common python library for DS.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dragonsun7/dsPyLib",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
