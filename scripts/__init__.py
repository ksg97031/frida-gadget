"""init file for scripts folder."""
from .logger import logger
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
INSTALLED_FRIDA_VERSION: str = __import__('frida').__version__  # Get installed frida version
logger.info("Auto-detected frida version: " + INSTALLED_FRIDA_VERSION)
