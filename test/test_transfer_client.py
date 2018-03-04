import json
import sys
import time
import unittest
from unittest import mock


requests_mock = mock.MagicMock()
# To avoid making an actual HTTP request
sys.modules['requests'] = requests_mock

from dts_client.__main__ import TransferClient


class Test_DTS_Client(unittest.TestCase):
    def setUp(self):
        self.last_payload = None
        self.last_interval = None
        self.call_count = 0
        self.expected_calls = 3
        self.database_interfacer = mock.MagicMock()
        self.client = None

    def setUp_database_interfacer(self):
        def mock_query(from_, to):
            self.assert_interval(from_, to)
            self.last_payload = dict(payload=int(time.time()))
            return self.last_payload

        self.database_interfacer.archive_query_interval.side_effect = mock_query

    def setUp_bad_database_interfacer(self):
        def mock_query(from_, to):
            self.call_count += 1
            if self.call_count >= self.expected_calls:
                self.client.stop()
            raise IOError()

        self.database_interfacer.archive_query_interval.side_effect = mock_query

    def setUp_server_send(self):
        def mock_post(*_, data, **__):
            self.call_count += 1
            self.assertEqual(json.dumps(self.last_payload), data)
            if self.call_count >= self.expected_calls:
                self.client.stop()

        global requests_mock
        requests_mock.post.side_effect = mock_post

    def assert_interval(self, from_, to):
        if (self.last_interval):
            self.assertAlmostEqual(from_ - self.last_interval[1], 0, delta=0.1)

        self.last_interval = (from_, to)

    @unittest.skip
    def test_start_interval(self):
        self.setUp_server_send()
        self.setUp_database_interfacer()
        self.client = TransferClient(self.database_interfacer,
                                     'localhost:99999',
                                     1)
        self.client.start()

    def test_database_error(self):
        self.setUp_server_send()
        self.setUp_bad_database_interfacer()
        self.client = TransferClient(self.database_interfacer,
                                     'localhost:99999',
                                     1)
        self.client.start()
