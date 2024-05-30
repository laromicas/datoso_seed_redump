"""ReDump Dat classes to parse different types of dat files."""
import re

from datoso.configuration import config
from datoso.repositories.dat_file import ClrMameProDatFile, XMLDatFile

EXPECTED_NAME_ARRAY_LENGTH = 2

class RedumpDat(XMLDatFile):
    """Redump XML Dat class."""

    seed: str = 'redump'

    def initial_parse(self) -> list:
        """Parse the dat file."""
        name = self.name

        suffixes = re.findall(r'\(.*?\)', self.full_name)
        name = name.replace(' '.join(suffixes), '').strip()
        name_array = name.split(' - ')

        if name_array[0] == 'Arcade':
            self.modifier = name_array.pop(0)

        if len(name_array) == 1:
            name_array.insert(0, None)
        elif len(name_array) > EXPECTED_NAME_ARRAY_LENGTH:
            name_array = ['-'.join(name_array[0:-1]), name_array[-1:][0]]

        company, system = name_array
        self.company = company
        self.system = system
        self.suffix = None

        self.suffixes = suffixes
        find_system = self.overrides()
        self.extra_configs(find_system)

        if self.modifier or self.system_type:
            self.prefix = config.get('PREFIXES', self.modifier or self.system_type, fallback='')
        else:
            self.prefix = None


        return [self.prefix, self.company, self.system, self.suffix, self.get_date()]

    def get_date(self) -> str:
        """Get the date from the dat file."""
        if self.full_name:
            result = re.findall(r'\(.*?\)', self.full_name)
            if result:
                self.date = result[len(result)-1][1:-1]
        elif self.file:
            result = re.findall(r'\(.*?\)', str(self.file))
            if result:
                self.date = result[len(result)-1][1:-1]
        return self.date


class RedumpBiosDat(ClrMameProDatFile):
    """Redump BIOS Dat class."""

    system_type: str = 'BIOS'
    seed: str = 'redump'

    def initial_parse(self) -> list:
        """Parse the dat file."""
        # pylint: disable=R0801
        name = self.name

        suffixes = re.findall(r'\(.*?\)', self.full_name)
        name = name.replace(' '.join(suffixes), '').strip()
        name_array = name.split(' - ')
        if name_array[-1:][0] in ('BIOS Images'):
            self.modifier = name_array.pop()
        else:
            self.modifier = 'Handheld'

        company, system = name_array

        self.company = company
        self.system = system
        self.suffix = None

        self.suffixes = suffixes

        if self.modifier or self.system_type:
            self.prefix = config.get('PREFIXES', self.modifier or self.system_type, fallback='')
        else:
            self.prefix = None

        return [self.prefix, self.company, self.system, self.suffix, self.get_date()]

    def get_date(self) -> str:
        """Get the date from the dat file."""
        if self.full_name:
            result = re.findall(r'\(.*?\)', self.full_name)
            if result:
                self.date = result[1][1:-1]
        elif self.file:
            result = re.findall(r'\(.*?\)', str(self.file))
            if result:
                self.date = result[1][1:-1]
        return self.date
