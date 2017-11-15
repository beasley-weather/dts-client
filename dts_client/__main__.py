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
                 database_file,
                 server_address,
                 interval=DEFAULT_INTERVAL):
        '''
        :param database_file:  Path to Weewx database
        :param server_address: Address for server
        :param interval:       Transfer interval (seconds)
        '''
        self._database_file = database_file
        self._server_address = server_address
        self._interval = interval
        self._db = weewx_orm.WeewxDB(database_file)

        self._last_query_time = time.time()

    def start(self):
        start_time = time.time()
        self._last_query_time = start_time
        time_now = start_time
        time.sleep(self._interval - (time_now - start_time) % self._interval)
        while True:
            data = self._load_last_interval_data()
            self._transfer_data(data)

            time_now = time.time()
            self._last_query_time = time_now
            time.sleep(self._interval -
                       (time_now - start_time) % self._interval)

    def _load_last_interval_data(self):
        from_ = round(self._last_query_time)
        to = round(time.time())
        print('Querying data between {} and {}'.format(
            unix_time_to_human(from_), unix_time_to_human(to)
        ))
        return self._db.archive_query_interval(from_, to)

    def _transfer_data(self, data):
        '''
        :param data: Binary data
        '''
        # Handle server unavailable
        # Serialize data
        requests.post(self._server_address, data=data)


if __name__ == '__main__':
    cli_args = args.parse()
    client = TransferClient(cli_args.database, cli_args.server,
                            cli_args.interval)
    client.start()
