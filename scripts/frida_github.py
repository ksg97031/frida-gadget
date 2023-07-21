"""Github module for download frida gadget library"""
# Base code is sourced from the GitHub repository of Objection.
# Source: https://github.com/sensepost/objection/blob/master/objection/utils/patchers/github.py
import lzma
from pathlib import Path
import requests

class FridaGithub:
    """ Interact with Github """

    GITHUB_LATEST_RELEASE = 'https://api.github.com/repos/frida/frida/releases/latest'
    GITHUB_TAGGED_RELEASE = 'https://api.github.com/repos/frida/frida/releases/tags/{tag}'

    # the 'context' of this Github instance
    gadget_version = None

    def __init__(self, gadget_version: str = None):
        """
            Init a new instance of Github
        """

        if gadget_version:
            self.gadget_version = gadget_version

        self.request_cache = {}

    def _call(self, endpoint: str) -> dict:
        """
            Make a call to Github and cache the response.

            :param endpoint:
            :return:
        """

        # return a cached response if possible
        if endpoint in self.request_cache:
            return self.request_cache[endpoint]

        # get a new response
        results = requests.get(endpoint, timeout=30).json()

        # cache it
        self.request_cache[endpoint] = results

        # and return it
        return results

    def get_latest_version(self) -> str:
        """
            Call Github and get the tag_name of the latest
            release.

            :return:
        """

        self.gadget_version = self._call(self.GITHUB_LATEST_RELEASE)['tag_name']

        return self.gadget_version

    def get_assets(self) -> dict:
        """
            Gets the assets for the currently selected gadget_version.

            :return:
        """

        assets = self._call(self.GITHUB_TAGGED_RELEASE.format(tag=self.gadget_version))

        if 'assets' not in assets:
            raise FileNotFoundError(
                f'Unable to determine assets for gadget version \'{self.gadget_version}\'. '
                'Are you sure this version is available on Github?')

        return assets['assets']

    def download_asset(self, url: str, output_file: str) -> None:
        """
            Download an asset from Github.

            :param url:
            :param output_file:
            :return:
        """

        assert output_file.endswith('.xz')
        filepath = Path(output_file)
        if filepath.exists() and filepath.stat().st_size > 0:
            return

        response = requests.get(url, timeout=600, stream=True)
        with open(output_file, 'wb') as asset:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    asset.write(chunk)

    def download_gadget_so(self, url, gadget_fullpath: str) -> str:
        """
            Download the gadget library from Github.

            :param gadget_path:
            :return:
        """

        assert gadget_fullpath.endswith('.so')
        if Path(gadget_fullpath).exists():
            return gadget_fullpath

        xz_gadget_fullpath = gadget_fullpath + ".xz"
        self.download_asset(url, xz_gadget_fullpath)

        with lzma.open(xz_gadget_fullpath, "rb") as lzma_file:
            decompressed_data = lzma_file.read()
        with open(gadget_fullpath, "wb") as gadget_file:
            gadget_file.write(decompressed_data)

        return gadget_fullpath
