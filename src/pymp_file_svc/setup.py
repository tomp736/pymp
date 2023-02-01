import os
from setuptools import find_packages
from setuptools import setup

setup(
    name="pymp_file_svc",
    description="",
    long_description=open("README.md").read(),
    url="",
    version="0.0.1",
    author="Thomas Pisula",
    author_email="tompisula@protonmail.com",
    packages=find_packages(exclude=["ez_setup"]),
    install_requires=open(
        os.path.join(os.path.dirname(__file__), "requirements.txt")
    ).readlines(),
    entry_points={"console_scripts": ["pymp_file_svc  = pymp_file_svc.__main__:main"]},
    license="AGPL3",
)