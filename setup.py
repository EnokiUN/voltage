import re

from setuptools import setup

version = ""
with open("voltage/__init__.py") as f:
    match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE)
    if match is not None:
        version = match.group(1)
    else:
        raise RuntimeError("version is not set")

requirements = []
with open("requirements.txt") as f:
    requirements = f.read().splitlines()


readme = ""
with open("README.rst") as f:
    readme = f.read()

setup(
    name="voltage",
    author="EnokiUN",
    url="https://github.com/EnokiUN/voltag",
    project_urls={
        "Documentation": "https://psup.readthedocs.io/en/latest/",
        "Issue tracker": "https://github.com/enokiun/voltage/issues",
    },
    version=version,
    license="MIT",
    packages=["voltage"],
    install_requires=requirements,
    description="A Simple Pythonic Asynchronous API wrapper for Revolt.",
    long_description=readme,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    python_requires=">=3.8.0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
)
