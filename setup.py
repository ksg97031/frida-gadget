import os
import sys
import setuptools

if sys.version_info < (3, 6):
    print("Unfortunately, your python version is not supported!\n" +
          "Please upgrade at least to Python 3.6!")
    sys.exit(1)

about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "scripts", "__version__.py"), "r", encoding="utf-8") as f:
    exec(f.read(), about)

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

requires = [
    'click',
    'androguard >= 4.0.0',
    'apk-signer',
    'pytest',
    'colorlog',
    'coverage',
    'requests',
]

setuptools.setup(
    name=about["__title__"],
    python_requires='>=3.6',
    version=about["__version__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    description=about["__description__"],
    install_requires=requires,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url=about["__url__"],
    packages=setuptools.find_packages(),
    package_data={
        'scripts': [
            "files/README.md",
        ]
    },
    entry_points={
        'console_scripts': ['frida-gadget = scripts.cli:run'],
    },
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
