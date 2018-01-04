# TODO
# Need a logging service to have a record of events
# save last query timestamp externally in case of restart

import time

import requests
import weewx_orm

from . import args
from .consts import DEFAULT_INTERVAL
from .util import unix_time_to_human


class TransferClient:
    def __init__(self,
                 database_interfacer,
                 server_send,
                 interval=DEFAULT_INTERVAL,
                 interval_start_time=time.time()):
        '''
        :param database_interfacer:  An object that knows how to query the database
        :param server_send:          Function to send data to a server
        :param interval:             Transfer interval (seconds)
        :param interval_start_time:  Start of first interval (seconds since epoch)
        '''
        self._is_running = True
        self._database_interfacer = database_interfacer
        self._server_send = server_send
        self._interval = interval
        self._last_query_time = interval_start_time

    def start(self):
        start_time = time.time()
        self._last_query_time = start_time
        time_now = start_time
        time.sleep(self._interval - (time_now - start_time) % self._interval)
        while self._is_running:
            data = self._load_last_interval_data()
            self._transfer_data(data)

            time_now = time.time()
            self._last_query_time = time_now
            time.sleep(self._interval -
                       (time_now - start_time) % self._interval)

    def stop(self):
        self._is_running = False

    def _load_last_interval_data(self):
        from_ = round(self._last_query_time)
        to = round(time.time())
        print('Querying data between {} ({}) and {} ({})'.format(
            unix_time_to_human(from_), from_, unix_time_to_human(to), to
        ))
        return self._database_interfacer.archive_query_interval(from_, to)

    def _transfer_data(self, data):
        '''
        :param data: Binary data
        '''
        # Handle server unavailable
        # Serialize data
        self._server_send(data)


def server_send(server_address):
    '''
    :param server_address: Address for server
    :throws: Network Exceptions
    '''
    def func(data):
        requests.post(server_address, data=data)

    return func


def create_client(server_address, database, interval, interval_start_time=None):
    '''
    :param server_address: Address for server
    :param database: Database name
    :param interval: Transfer interval
    :param interval_start_time:  Start of first interval (seconds since epoch)
    '''
    database_interfacer = weewx_orm.WeewxDB(database)
    if interval_start_time is None:
        return TransferClient(database_interfacer,
                              server_send(server_address),
                              interval,
                              interval_start_time)
    else:
        return TransferClient(database_interfacer,
                              server_send(server_address),
                              interval)

if __name__ == '__main__':
    cli_args = args.parse()
    client = create_client(cli_args.server, cli_args.database, cli_args.interval)
    client.start()
