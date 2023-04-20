
import os
import shutil
import zipfile
from datetime import datetime
from html.parser import HTMLParser
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datoso_seed_redump import __preffix__

from datoso.configuration.folder_helper import Folders

# TMP = 'tmp'
# WORK_FOLDER = os.getenv('WORK_FOLDER', os.getcwd())
# SEED_NAME = os.getenv('SEED_NAME', os.path.basename(os.getcwd()))
# TMP_DIR = os.path.join(WORK_FOLDER, os.getenv('TMP_FOLDER', 'tmp'))
# TMP_REDUMP = os.path.join(TMP_DIR, SEED_NAME)
# TMP_DATS = os.path.join(TMP_REDUMP, 'dats')

MAIN_URL = 'http://redump.org'
DOWNLOAD_URL = 'http://redump.org/downloads/'
TYPES = ["datfile", "cues", "gdi", "sbi"]


# def mktmpdirs():
#     os.makedirs(TMP_DIR, exist_ok=True)
#     os.makedirs(TMP_REDUMP, exist_ok=True)
#     os.makedirs(TMP_DATS, exist_ok=True)

# def clean():
#     # delete old files
#     os.system(f'rm -rf {TMP_REDUMP}/*')

class MyHTMLParser(HTMLParser):
    dats = {}
    rootpath = MAIN_URL
    types = TYPES
    folder_helper = None

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
                    # savefile(self.folder_helper, output, self.rootpath+href)
                    self.add_to_dats(output, self.rootpath+href)

    def add_to_dats(self, folder, href):
        self.dats[href] = folder

def download_dats(folder_helper):
    def download_dat(href, folder):
        print(f'Downloading {href}')
        tmp_filename, headers = urllib.request.urlretrieve(href)
        local_filename = os.path.join(folder_helper.dats, folder, headers.get_filename())
        shutil.move(tmp_filename, local_filename)
        if folder in ['datfile']:
            with zipfile.ZipFile(local_filename, 'r') as zip_ref:
                zip_ref.extractall(os.path.join(folder_helper.dats, folder))
            os.remove(local_filename)

    print('Downloading Redump HTML')
    red = urllib.request.urlopen(DOWNLOAD_URL)
    redumphtml = red.read()

    print('Parsing Redump HTML')
    parser = MyHTMLParser()
    parser.folder_helper = folder_helper
    parser.feed(str(redumphtml))

    print('Downloading new dats')

    with ThreadPoolExecutor(max_workers=10) as executor:
        for href, folder in parser.dats.items():
            executor.submit(download_dat, href, folder)

    print('Zipping files')
    backup_daily_name = f'redump-{datetime.now().strftime("%Y-%m-%d")}.zip'
    with zipfile.ZipFile(os.path.join(folder_helper.backup, backup_daily_name), 'w') as zip_ref:
        for root, dirs, files in os.walk(folder_helper.dats):
            for file in files:
                zip_ref.write(os.path.join(root, file), arcname=os.path.join(root.replace(folder_helper.dats, ''), file), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

def fetch():
    # mktmpdirs()
    NEWTYPES = TYPES+['bios']
    folder_helper = Folders(seed=__preffix__, extras=NEWTYPES)
    folder_helper.clean_dats()
    folder_helper.create_all()
    # clean()
    download_dats(folder_helper)
