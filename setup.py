import sys
import setuptools

if sys.version_info < (3, 6):
    print("Unfortunately, your python version is not supported!\n" +
          "Please upgrade at least to Python 3.6!")
    sys.exit(1)

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

requires = [
    'click',
    'androguard',
    'apk-signer',
    'pytest',
    'colorlog',
    'coverage',
    'requests',
]

setuptools.setup(
    name="frida-gadget",
    python_requires='>=3.6',
    version="1.2.0",
    author="ksg97031",
    author_email="ksg97031@gmail.com",
    description="Frida gadget into an APK",
    install_requires=requires,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/ksg97031/frida-gadget",
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
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
