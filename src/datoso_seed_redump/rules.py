from datoso_seed_redump.dats import RedumpBiosDat, RedumpDat

rules = [
    {
        'name': 'Redump BIOS DAT',
        '_class': RedumpBiosDat,
        'seed': 'redump',
        'priority': 60,
        'rules': [
            {
                'key': 'author',
                'operator': 'contains',
                'value': 'redump.org',
            },
            {
                'key': 'description',
                'operator': 'contains',
                'value': 'BIOS Images',
                'case_sensitive': False,
            },
        ],
    },
    {
        'name': 'Redump DAT',
        '_class': RedumpDat,
        'seed': 'redump',
        'priority': 50,
        'rules': [
            {
                'key': 'url',
                'operator': 'contains',
                'value': 'redump.org',
            },
            {
                'key': 'homepage',
                'operator': 'eq',
                'value': 'redump.org',
            },
            {
                'key': 'description',
                'operator': 'contains',
                'value': 'Discs',
                'case_sensitive': False,
            },
        ],
    },
]


def get_rules():
    return rules
