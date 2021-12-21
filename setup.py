"""SDA sftp Uploader Application with both GUI and CLI interfaces."""

from setuptools import setup
from sda_uploader import __version__

setup(
    name="sda_uploader",
    version=__version__,
    license="Apache-2.0",
    author="CSC - IT Center for Science Ltd.",
    author_email="",
    description="Encryption and uploading tool.",
    long_description="",
    packages=["sda_uploader"],
    entry_points={"console_scripts": ["sdagui=sda_uploader.__main__:main", "sdacli=sda_uploader.cli:main"]},
    platforms="any",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
    ],
    install_requires=["crypt4gh", "paramiko"],
)
