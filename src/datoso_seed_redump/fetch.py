
import os
from html.parser import HTMLParser
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datoso_seed_redump import __preffix__

from datoso.configuration import config, folder_helper, logger
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
                    savefile(self.folder_helper, output, self.rootpath+href)


def savefile(folder_helper, output, href):
    with open(os.path.join(folder_helper.download, f'{output}.txt'), 'a+') as fp:
        fp.write(href+"\n")


def main(folder_helper):
    def download_dats(file):
        new_path = os.path.join(folder_helper.dats, file)
        os.makedirs(new_path, exist_ok=True)
        os.system(f'cd {new_path} && aria2c --file-allocation=prealloc -i ../../{file}.txt')
        # extract dat files
        if file in ['datfile']:
            os.system(f'cd {new_path} && unzip -o \'*.zip\'')
            os.system(f'cd {new_path} && rm *.zip')

    red = urllib.request.urlopen(DOWNLOAD_URL)

    redumphtml = red.read()

    print('Parsing Redump HTML')
    parser = MyHTMLParser()
    parser.folder_helper = folder_helper
    parser.feed(str(redumphtml))

    print('Downloading new dats')
    NEWTYPES = TYPES+['bios']

    with ThreadPoolExecutor(max_workers=10) as executor:
        for file in NEWTYPES:
            executor.submit(download_dats, file)

    # zip files in TMP_DIR with 7z
    print('Zipping files')
    os.system(f'cd {folder_helper.download} && 7z a -tzip redump.zip redump')

def fetch():
    # mktmpdirs()
    folder_helper = Folders(seed=__preffix__)
    folder_helper.clean_dats()
    folder_helper.create_all()
    # clean()
    main(folder_helper)
