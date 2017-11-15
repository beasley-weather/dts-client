import argparse

from .consts import DEFAULT_INTERVAL


def parse():
    parser = argparse.ArgumentParser(
        description='Beasley Weather Station Data Transfer Client'
    )
    parser.add_argument('database', help='Weewx database.')
    parser.add_argument('server', help='Data Transfer Server\'s address.')
    parser.add_argument('-i', '--interval', type=int,
                        help='Query and transfer interval.', default=DEFAULT_INTERVAL)
    return parser.parse_args()
