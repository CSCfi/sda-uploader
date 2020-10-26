from setuptools import setup

setup(
    name="sda_uploader",
    version="0.1.0",
    license="Apache-2.0",
    author="CSC - IT Center for Science Ltd.",
    author_email="",
    description="Encryption and uploading tool.",
    long_description="",
    packages=["sda_uploader"],
    entry_points={"console_scripts": ["sdagui=sda_uploader.__main__:main"]},
    platforms="any",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.6",
    ],
    install_requires=["crypt4gh", "paramiko"],
)
