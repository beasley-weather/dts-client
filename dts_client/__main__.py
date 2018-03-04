import json
import logging
import time
from os import environ as env
from traceback import print_exc
from typing import Dict

import requests
import weewx_orm

from .consts import DEFAULT_INTERVAL
from .util import unix_time_to_human


SECS_IN_DAY = 24 * 3600


_logger = logging.getLogger(__name__)


class TransferClient:
    def __init__(self,
                 database_interfacer,
                 server_address,
                 interval=DEFAULT_INTERVAL,
                 interval_start_time=time.time() - SECS_IN_DAY,
                 *,
                 address_protocol='http'):
        '''
        :param database_interfacer:  An object that knows how to query the database
        :param server_send:          Function to send data to a server
        :param interval:             Transfer interval (seconds)
        :param interval_start_time:  Start of first interval (seconds since epoch)
        :param address_protocol:     If server_send does not specify a protocol,
           it can be overridden by specifying an address_protocol argument.
           (default: http)
        '''
        self._is_running = True
        self._database_interfacer = database_interfacer
        if ('://' not in server_address):
            server_address = f'{address_protocol}://{server_address}'
        self._server_address = server_address
        self._interval = int(interval)
        self._last_query_time = interval_start_time

    def start(self):
        start_time = time.time()
        time_now = start_time

        while self._is_running:
            try:
                data = self._load_last_interval_data(round(time_now))
                try:
                    self._transfer_data(data)
                except IOError as exc:
                    _logger.error(
                        f'Unable to transfer data to {self._server_address}: {exc}'
                    )
            except IOError as exc:
                _logger.error(
                    f'Unable to query data for the interval '
                    f'({round(self._last_query_time)}, {round(time_now)}): {exc}'
                )


            time.sleep(self._interval - (time_now - start_time) % self._interval)
            self._last_query_time = time_now
            time_now = time.time()

    def stop(self):
        self._is_running = False

    def _load_last_interval_data(self, to: int) -> Dict:
        '''
        :to: End of interval
        :return:
        :raises: IOError if query fails
        '''
        from_ = max(to - SECS_IN_DAY, round(self._last_query_time))
        _logger.info(
            'Querying data between {} ({}) and {} ({})'
                .format(unix_time_to_human(from_), from_, unix_time_to_human(to), to)
        )

        try:
            data = self._database_interfacer.archive_query_interval(from_, to)
        except IOError as exc:
            raise exc

        return json.dumps(data)

    def _transfer_data(self, data, tries = 3) -> None:
        '''
        :param data: Binary data
        :param tries: Number of attempt to transfer data before giving up
        :raise: IOError if unable to transfer data
        '''
        for i in range(3):
            try:
                requests.post(self._server_address, data=data)
                return
            except requests.RequestException:
                print_exc()

        raise IOError(f'Unable to transfer data. {tries} attempts made.')


def create_client(server_address, database, interval, interval_start_time=None):
    '''
    :param server_address: Address for server
    :param database: Database name
    :param interval: Transfer interval
    :param interval_start_time:  Start of first interval (seconds since epoch)
    '''
    database_interfacer = weewx_orm.WeewxDB(database)
    if interval_start_time is not None:
        return TransferClient(database_interfacer,
                              server_address,
                              interval,
                              interval_start_time)
    else:
        return TransferClient(database_interfacer,
                              server_address,
                              interval)


if __name__ == '__main__':
    client = create_client(env['DTS_SERVER'], env['WEEWX_DATABASE'], env['DTS_INTERVAL'])
    client.start()
