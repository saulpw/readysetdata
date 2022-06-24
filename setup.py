# SPDX-License-Identifier:

from setuptools import setup


def readme():
    with open("README.md") as f:
        return f.read()

def requirements():
    with open("requirements.txt") as f:
        return f.read().split("\n")


setup(
        name="readysetdata",
        version="",
        description="A collection of tools to convert select datasets into ready-to-use formats.",
        long_description=readme(),
        long_description_content_type="text/markdown",
        classifiers=[
            "Development Status :: 4 - Beta",
            "Programming Language :: Python ::3",
        ],
        keywords="datasets readysetdata",
        author="Saul Pwanson",
        url="https://github.com/saulpw/readysetdata",
        python_requires=">=3.8",
        py_modules=["readysetdata"],
        packages=["readysetdata"],
        scripts=["scripts/remote-unzip.py"],
        install_requires=requirements(),
)
