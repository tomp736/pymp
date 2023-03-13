import os
import json
from typing import List
from unittest import TestCase
from pymp_core.app.config import ServiceConfig, PympServerRoles
from pymp_core.app.config_source import JsonServiceConfigReader

class TestJsonServiceConfigReader(TestCase):
    def setUp(self):
        self.config_path = 'test_config.json'
        self.config_data = [
            {
                "id": "service1",
                "roles": 6,
                "proto": "http",
                "host": "localhost",
                "port": 8080
            },
            {
                "id": "service2",
                "roles": 96,
                "proto": "https",
                "host": "127.0.0.1",
                "port": 8443
            }
        ]
        with open(self.config_path, 'w') as f:
            json.dump(self.config_data, f)

    def tearDown(self):
        os.remove(self.config_path)

    def test_load_config(self):
        reader = JsonServiceConfigReader(self.config_path)
        configs = reader.load_config()
        self.assertEqual(len(configs), 2)
        self.assertEqual(configs[0].id, "service1")
        self.assertEqual(configs[0].roles, PympServerRoles.MEDIA_API | PympServerRoles.META_API)
        self.assertEqual(configs[0].host, "localhost")
        self.assertEqual(configs[0].proto, "http")
        self.assertEqual(configs[0].port, 8080)
        self.assertEqual(configs[1].id, "service2")
        self.assertEqual(configs[1].roles, PympServerRoles.FFMPEG_SVC | PympServerRoles.MEDIAREGISTRY_SVC)
        self.assertEqual(configs[1].host, "127.0.0.1")
        self.assertEqual(configs[1].proto, "https")
        self.assertEqual(configs[1].port, 8443)


    def test_load_config_empty(self):
        reader = JsonServiceConfigReader("invalid")
        configs = reader.load_config()
        self.assertEqual(len(configs), 0)