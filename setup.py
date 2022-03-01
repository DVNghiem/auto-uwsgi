from setuptools import setup

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), 'r', encoding='utf-8') as f:
    long_description = f.read()

# This call to setup() does all the work
setup(
    name="auto-uwsgi",
    version="1.0.0",
    description="""Auto deploy django project on linux using nginx and uwsgi""",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nghiemIUH/auto-uwsgi",
    author="Van Nghiem",
    author_email="vannghiem848@gmail.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ],
    packages=["auto_uwsgi"]
)