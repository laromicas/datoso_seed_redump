from datoso_seed_redump.dats import RedumpBiosDat, RedumpDat

# ruff: noqa: ERA001

actions = {
    '{dat_origin}/bios': [
        {
            'action': 'LoadDatFile',
            '_class': RedumpBiosDat,
        },
        {
            'action': 'DeleteOld',
            'folder': '{dat_destination}',
        },
        {
            'action': 'Copy',
            'folder': '{dat_destination}',
        },
        {
            'action': 'SaveToDatabase',
        },
    ],
    # "{dat_origin}/cues": [
    #     {
    #         "action": "Copy",
    #         "folder": "ToSort",
    #         "destination": "tmp/cues"
    #     }
    # ],
    '{dat_origin}/gdi': [],
    '{dat_origin}/datfile': [
        {
            'action': 'LoadDatFile',
            '_class': RedumpDat,
        },
        {
            'action': 'DeleteOld',
            'folder': '{dat_destination}',
        },
        {
            'action': 'Copy',
            'folder': '{dat_destination}',
        },
        {
            'action': 'MarkMias',
        },
        {
            'action': 'SaveToDatabase',
        },
    ],
    '{dat_origin}/sbi': [],
}

def get_actions():
    return actions
