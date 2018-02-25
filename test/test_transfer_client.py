import json
import time
import unittest
from unittest import mock

from dts_client.__main__ import TransferClient


class Test_DTS_Client(unittest.TestCase):
    def setUp(self):
        self.setUp_server_send()
        self.setUp_database_interfacer()
        self.last_payload = None
        self.last_interval = None
        self.interval = 1
        self.call_count = 0
        self.expected_calls = 3
        self.client = TransferClient(self.database_interfacer,
                                     self.server_send,
                                     self.interval)

    def setUp_database_interfacer(self):
        def mock_query(from_, to):
            self.assert_interval(from_, to)
            self.last_payload = dict(payload=int(time.time()))
            return self.last_payload

        dbi = mock.MagicMock()
        self.database_interfacer = dbi
        dbi.archive_query_interval.side_effect = mock_query

    def setUp_server_send(self):
        def mock_server_send(data):
            self.call_count += 1
            self.assertEqual(json.dumps(self.last_payload), data)
            if self.call_count >= self.expected_calls:
                self.client.stop()

        self.server_send = mock.MagicMock(side_effect=mock_server_send)

    def test_start_interval(self):
        self.client.start()

    def assert_interval(self, from_, to):
        if (self.last_interval):
            self.assertAlmostEqual(from_ - self.last_interval[1], 0, delta=0.1)

        self.last_interval = (from_, to)
