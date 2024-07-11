"""Argument parser for Redump seed."""
from argparse import ArgumentParser, Namespace

from datoso.configuration import config


def seed_args(parser: ArgumentParser) -> ArgumentParser:
    """Add seed arguments to the parser."""
    headless = parser.add_mutually_exclusive_group()
    headless.add_argument('-dl', '--downloader', help='Select downloader utility',
                          choices=['wget', 'curl', 'aria2c', 'urllib'], default=None)
    return parser

def post_parser(args: Namespace) -> None:
    """Post parser actions."""
    if getattr(args, 'downloader', None) is not None:
        config.set('REDUMP', 'DownloadUtility', args.downloader)

def init_config() -> None:
    """Initialize the configuration."""
    if not config.has_section('REDUMP'):
        config['REDUMP'] = {
            'DownloadUtility': 'wget',
        }
