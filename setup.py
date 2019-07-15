import sys
import setuptools

if sys.version_info < (3, 7):
    print("Unfortunately, your python version is not supported!\n"
          + "Please upgrade at least to Python 3.7!")
    sys.exit(1)

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="frida-gadget",
    python_requires='>=3.7',
    version="0.0.1",
    author="ksg97031",
    author_email="ksg97031@gmail.com",
    description="Sign the apk file",
    install_requires=['click', 'pathlib', 'frida==12.6.10', 'androguard'],
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/ksg97031/frida-gadget",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'frida-gadget = scripts.cli:run'
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
