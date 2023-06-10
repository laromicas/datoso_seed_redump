
import os
import shutil
import zipfile
from datetime import datetime
from html.parser import HTMLParser
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datoso.configuration.folder_helper import Folders
from datoso.helpers import Bcolors
from datoso_seed_redump import __preffix__
import logging

MAIN_URL = 'http://redump.org'
DOWNLOAD_URL = 'http://redump.org/downloads/'
TYPES = ["datfile", "cues", "gdi", "sbi"]

class MyHTMLParser(HTMLParser):
    dats = {}
    rootpath = MAIN_URL
    types = TYPES

    def handle_starttag(self, tag, attrs):
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
        self.dats[href] = folder

def download_dats(folder_helper):
    done = 0
    def download_dat(href, folder): #TODO: change to asyncio
        nonlocal done
        # print(f'Downloading {href}')
        try:
            tmp_filename, headers = urllib.request.urlretrieve(href)
        except Exception as e:
            logging.error(f'Error downloading {DOWNLOAD_URL}: {e}')
            print(f'Error downloading {href}')
            return
        local_filename = os.path.join(folder_helper.dats, folder, headers.get_filename())
        shutil.move(tmp_filename, local_filename)
        if folder in ['datfile']:
            with zipfile.ZipFile(local_filename, 'r') as zip_ref:
                zip_ref.extractall(os.path.join(folder_helper.dats, folder))
            os.remove(local_filename)
        done += 1
        print_progress(done)

    print('Downloading Redump HTML')
    try:
        red = urllib.request.urlopen(DOWNLOAD_URL)
    except Exception as e:
        logging.error(f'Error downloading {DOWNLOAD_URL}: {e}')
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

    with ThreadPoolExecutor(max_workers=10) as executor:
        for href, folder in parser.dats.items():
            executor.submit(download_dat, href, folder)

    print('\nZipping files for backup')
    backup_daily_name = f'redump-{datetime.now().strftime("%Y-%m-%d")}.zip'
    with zipfile.ZipFile(os.path.join(folder_helper.backup, backup_daily_name), 'w') as zip_ref:
        for root, dirs, files in os.walk(folder_helper.dats):
            for file in files:
                zip_ref.write(os.path.join(root, file), arcname=os.path.join(root.replace(folder_helper.dats, ''), file), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

def fetch():
    NEWTYPES = TYPES+['bios']
    folder_helper = Folders(seed=__preffix__, extras=NEWTYPES)
    folder_helper.clean_dats()
    folder_helper.create_all()
    download_dats(folder_helper)
