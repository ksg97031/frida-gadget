"""Github module for download frida gadget library"""
# Base code is sourced from the GitHub repository of Objection.
# Source: https://github.com/sensepost/objection/blob/master/objection/utils/patchers/github.py
from pathlib import Path
import hashlib
import os
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
        filepath = Path(output_file)
        if filepath.exists() and filepath.stat().st_size > 0:
            return

        response = requests.get(url, timeout=600, stream=True)
        with open(output_file, 'wb') as asset:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    asset.write(chunk)

    def download_signer_jar(self, assets: list, signer_fullpath: str) -> str:
        """
            Download the signer jar library from Github.

            :param assets:
            :param signer_path:
            :return:
        """
        assert len(assets) == 2, 'Unable to determine the correct asset to download.'
        assert signer_fullpath.endswith('.jar'), 'Signer path must end with .jar'

        checksum_download_url = assets[0]['browser_download_url']
        uber_apk_signer_download_url = assets[1]['browser_download_url']
        if assets[1]['name'] == 'checksum-sha256.txt':
            checksum_download_url, uber_apk_signer_download_url = \
                uber_apk_signer_download_url, checksum_download_url
        assert uber_apk_signer_download_url.endswith('.jar'), 'Download URL must end with .jar'
    
        signer_path = Path(signer_fullpath)
        download_directory = signer_path.parent
        if signer_path.exists():
            return signer_fullpath

        if not download_directory.exists():
            download_directory.mkdir(parents=True, exist_ok=True)        

        check_sum_fullpath = signer_fullpath[:-4] + '.sha256'
        self.download_asset(checksum_download_url, check_sum_fullpath)

        with open(check_sum_fullpath, 'rb') as checksum_file:
            checksum = checksum_file.read(64).decode('utf-8')
        
        self.download_asset(uber_apk_signer_download_url, signer_fullpath)
        with open(signer_fullpath, 'rb') as signer_file:
            signer_data = signer_file.read()
            signer_hash = hashlib.sha256(signer_data).hexdigest()
        
        if checksum != signer_hash:
            os.remove(signer_fullpath)
            os.remove(check_sum_fullpath)
            raise ValueError('The downloaded uber-apk-signer-*.jar file does not match the checksum.')

        return signer_fullpath
