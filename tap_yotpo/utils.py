"""
This module contains utilities.
"""
import argparse
import datetime
import os

from singer import load_json, Catalog
from singer.utils import check_config


DATE_FORMAT = '%Y-%m-%d'


class SecretNotFound(Exception):
    pass


def parse_args(required_config_keys):
    """Parse standard command-line args.

    Parses the command-line arguments mentioned in the SPEC and the
    BEST_PRACTICES documents:

    -c,--config     Config file
    --start-date    Start date. Required when config file is not used. Format: YYYY-mm-dd.
    --email-stats-lookback-days [0-365]
                    Days to look back for email stats. Set thru flag when
                    config file is not used.
    --reviews-lookback-days [0-365]
                    Days to look back for reviews. Set thru flag when
                    config file is not used.
    -s,--state      State file
    -d,--discover   Run in discover mode
    -p,--properties Properties file: DEPRECATED, please use --catalog instead
    --catalog       Catalog file

    Returns the parsed args object from argparse. For each argument that
    point to JSON files (config, state, properties), we will automatically
    load and parse the JSON file.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--config',
        help='Config file',
        required=False)
    parser.add_argument(
        '--start-date',
        help='Start date. Required when config file is not used. Format: YYYY-mm-dd.')
    parser.add_argument(
        '--email-stats-lookback-days',
        help='Days to look back for email stats. Set thru flag when config file is not used.',
        type=int,
        choices=range(0, 365),  # TODO validate date range
        metavar='[0-365]',
    )
    parser.add_argument(
        '--reviews-lookback-days',
        help='Days to look back for reviews. Set thru flag when config file is not used.',
        type=int,
        choices=range(0, 365),
        metavar='[0-365]',
    )
    parser.add_argument(
        '-s', '--state',
        help='State file')
    parser.add_argument(
        '-p', '--properties',
        help='Property selections: DEPRECATED, Please use --catalog instead')
    parser.add_argument(
        '--catalog',
        help='Catalog file')
    parser.add_argument(
        '-d', '--discover',
        action='store_true',
        help='Do schema discovery')
    args = parser.parse_args()
    if args.config:
        setattr(args, 'config_path', args.config)
        args.config = load_json(args.config)
    else:
        # validate argument
        get_date_from_str(args.start_date)
        args.config = {
            'api_key': get_secret('YOTPO_API_KEY'),
            'api_secret': get_secret('YOTPO_SECRET_TOKEN'),
            'start_date': args.start_date
        }
        if args.email_stats_lookback_days:
            args.config['email_stats_lookback_days'] = args.email_stats_lookback_days
        if args.reviews_lookback_days:
            args.config['reviews_lookback_days'] = args.reviews_lookback_days
    if args.state:
        setattr(args, 'state_path', args.state)
        args.state = load_json(args.state)
    else:
        args.state = {}
    if args.properties:
        setattr(args, 'properties_path', args.properties)
        args.properties = load_json(args.properties)
    if args.catalog:
        setattr(args, 'catalog_path', args.catalog)
        args.catalog = Catalog.load(args.catalog)
    check_config(args.config, required_config_keys)
    return args


def get_secret(secret_key: str) -> str:
    """Get secret from environment variable.

    :raises SecretNotFound:
    """
    val = os.environ.get(secret_key)
    if not val:
        raise SecretNotFound(f'Environment variable {secret_key} does not exist.')
    return val


def get_date_from_str(date_str: str, date_format: str = DATE_FORMAT) -> datetime.date:
    """ Returns date instance from date string.

    :raises ValueError:
    """
    return datetime.datetime.strptime(date_str, date_format).date()
