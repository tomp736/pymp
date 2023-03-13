import os
import unittest

from pymp_core.app.config_source import EnvironmentConfigSource


class EnvironmentConfigSourceTest(unittest.TestCase):
    def setUp(self):
        os.environ['SERVER_ID'] = 'test_server'
        os.environ['SERVER_ROLES'] = '14'
        os.environ['SERVER_HOST'] = 'test_host'
        os.environ['SERVER_PROTO'] = 'https'
        os.environ['SERVER_PORT'] = '8080'

    def tearDown(self):
        del os.environ['SERVER_ID']
        del os.environ['SERVER_ROLES']
        del os.environ['SERVER_HOST']
        del os.environ['SERVER_PROTO']
        del os.environ['SERVER_PORT']

    def test_load_server_config(self):
        reader = EnvironmentConfigSource()
        config = reader.get_values()

        self.assertEqual(config['SERVER_ID'], 'test_server')
        self.assertEqual(config['SERVER_ROLES'], '14')
        self.assertEqual(config['SERVER_HOST'], 'test_host')
        self.assertEqual(config['SERVER_PROTO'], 'https')
        self.assertEqual(config['SERVER_PORT'], '8080')
