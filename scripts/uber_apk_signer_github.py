"""Github module for download frida gadget library"""
# Base code is sourced from the GitHub repository of Objection.
# Source: https://github.com/sensepost/objection/blob/master/objection/utils/patchers/github.py
from pathlib import Path
import requests

class UberApkSignerGithub:
    """ Interact with Github """

    GITHUB_LATEST_RELEASE = 'https://api.github.com/repos/patrickfav/uber-apk-signer/releases/latest'

    # the 'context' of this Github instance
    signer_version = None

    def __init__(self, signer_version: str = None):
        """
            Init a new instance of Github
        """

        if signer_version:
            self.signer_version = signer_version

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

    def get_assets(self) -> dict:
        """
            Gets the assets for the currently selected signer_version.

            :return:
        """

        assets = self._call(self.GITHUB_LATEST_RELEASE)

        self.signer_version = assets['tag_name'][1:]

        if 'assets' not in assets:
            raise FileNotFoundError(
                f'Unable to determine assets for signer version \'{self.signer_version}\'. '
                'Are you sure this version is available on Github?')

        return assets['assets']

    def download_asset(self, url: str, output_file: str) -> None:
        """
            Download an asset from Github.

            :param url:
            :param output_file:
            :return:
        """

        assert output_file.endswith('.jar')
        filepath = Path(output_file)
        if filepath.exists() and filepath.stat().st_size > 0:
            return

        response = requests.get(url, timeout=600, stream=True)
        with open(output_file, 'wb') as asset:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    asset.write(chunk)

    def download_signer_jar(self, url, signer_fullpath: str) -> str:
        """
            Download the signer jar library from Github.

            :param signer_path:
            :return:
        """

        assert signer_fullpath.endswith('.jar')
        signer_path = Path(signer_fullpath)
        download_directory = signer_path.parent
        if signer_path.exists():
            return signer_fullpath

        if not download_directory.exists():
            download_directory.mkdir(parents=True, exist_ok=True)

        self.download_asset(url, signer_fullpath)

        return signer_fullpath
