
import logging
import os
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

from dateutil import tz

from datoso.configuration import config
from datoso.configuration.folder_helper import Folders
from datoso.helpers import Bcolors
from datoso.helpers.download import downloader
from datoso_seed_redump import __prefix__

MAIN_URL = 'http://redump.org'
DOWNLOAD_URL = 'http://redump.org/downloads/'
TYPES = ['datfile', 'cues', 'gdi', 'sbi']
NEWTYPES = [*TYPES, 'bios']

class MyHTMLParser(HTMLParser):
    """A custom HTML parser for parsing Redump HTML."""
    dats: dict | None = None
    rootpath = MAIN_URL
    types = TYPES

    def handle_starttag(self, tag: str, attrs: dict) -> None:
        """Handle the start tag of an HTML element.

        Args:
        ----
            tag (str): The name of the tag.
            attrs (dict): A dictionary of the tag's attributes.

        """
        if tag == 'a':
            taga = dict(attrs)
            if 'href' in taga:
                href = taga['href']
                hrefsplit = href.split('/')
                if len(hrefsplit) > 1 and hrefsplit[1] in self.types:
                    output = hrefsplit[1]
                    if 'bios' in href:
                        output = 'bios'
                    self.add_to_dats(output, self.rootpath+href)

    def add_to_dats(self, folder, href):
        if self.dats is None:
            self.dats = {}
        self.dats[href] = folder

def download_dats(folder_helper):
    done = 0
    def download_dat(href, folder): # TODO(laromicas): change to asyncio
        nonlocal done
        local_filename = downloader(url=href, destination=folder_helper.dats / folder, filename_from_headers=True)
        if folder in ['datfile']:
            with zipfile.ZipFile(local_filename, 'r') as zip_ref:
                zip_ref.extractall(folder_helper.dats / folder)
            Path.unlink(local_filename)
        done += 1
        print_progress(done)

    print('Downloading Redump HTML')
    try:
        red = urllib.request.urlopen(DOWNLOAD_URL)  # noqa: S310
    except Exception:
        logging.exception('Error downloading %s', DOWNLOAD_URL)
        print(f'{Bcolors.ERROR}Error downloading {DOWNLOAD_URL}. Skipping redump.{Bcolors.ENDC}')
        return
    redumphtml = red.read()

    print('Parsing Redump HTML')
    parser = MyHTMLParser()
    parser.feed(str(redumphtml))

    print('Downloading new dats')
    total_dats = len(parser.dats)

    def print_progress(done):
        print(f'  {done}/{total_dats} ({round(done/total_dats*100, 2)}%)', end='\r')

    with ThreadPoolExecutor(max_workers=int(config.get('DOWNLOAD', 'Workers', fallback=10))) as executor:
        futures = [
            executor.submit(download_dat, href, folder) for href, folder in parser.dats.items()
        ]
        for future in futures:
            future.result()

    print('\nZipping files for backup')
    backup_daily_name = f'redump-{datetime.now(tz.tzlocal()).strftime("%Y-%m-%d")}.zip'
    with zipfile.ZipFile(folder_helper.backup / backup_daily_name, 'w') as zip_ref:
        for root, _, files in os.walk(folder_helper.dats):
            for file in files:
                zip_ref.write(Path(root) / file, arcname=Path(root).relative_to(folder_helper.dats) / file,
                              compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

def fetch():
    folder_helper = Folders(seed=__prefix__, extras=NEWTYPES)
    folder_helper.clean_dats()
    folder_helper.create_all()
    download_dats(folder_helper)
