"""Module to install missing packages."""
import pip


def import_or_install(package):
    """Function to install missing packages.

    Args:
        package (string): Name of the package to install.
    """
    try:
        __import__(package)
    except ImportError:
        pip.main(['install', '--user', package])


import_or_install('frida')  # Install missing packages
INSTALLED_FRIDA_VERSION: str = __import__('frida').__version__
