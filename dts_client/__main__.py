# Need a logging service to have a record of events
import time

import requests


DEFAULT_INTERVAL = 3600  # 1 hour


class TransferAgent:
    def __init__(self, server_address, interval=DEFAULT_INTERVAL):
        '''
        :param server:   Address for server
        :param interval: Transfer interval (seconds)
        '''
        self._interval = interval
        self._server_address = server_address

    def start(self):
        time_start = time.time()
        while True:
            data = self._load_latest_data()
            self._transfer_data(data)

            time_now = time.time()
            time.sleep(self._interval - (time_now - time_start) % self._interval)

    def _load_latest_data(self):
        # Use weewx ORM library to load data
        pass

    def _transfer_data(self, data):
        '''
        :param data: Binary data
        '''
        requests.post(self._server_address, data=data)
