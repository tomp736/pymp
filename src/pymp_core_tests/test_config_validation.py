import logging
import os
import unittest
from unittest.mock import MagicMock

from pymp_core.app.config import MediaConfig
from pymp_core.app.config_factory import ConfigFactory
from pymp_core.app.config_source import EnvironmentConfigSource, RuntimeConfigSource


class TestMediaConfig(unittest.TestCase):
    def setUp(self):
        self.config = MediaConfig()
        self.config.media_path = "/tmp/test_media_path"
        self.config.index_path = "/tmp/test_index_path"
        self.config.media_chunk_size = 2 ** 22
        self.config.thumb_chunk_size = 2 ** 20

    def test_load_method(self):
        kwargs = {
            'media_path': '/tmp/new_media_path',
            'index_path': '/tmp/new_index_path',
            'media_chunk_size': '1048576',
            'thumb_chunk_size': '524288'
        }
        self.config.load(kwargs)
        self.assertEqual(self.config.media_path, '/tmp/new_media_path')
        self.assertEqual(self.config.index_path, '/tmp/new_index_path')
        self.assertEqual(self.config.media_chunk_size, 1048576)
        self.assertEqual(self.config.thumb_chunk_size, 524288)

    def test_load_config_method(self):
        config: Dict[str, str] = {
            'media_path': '/tmp/new_media_path',
            'index_path': '/tmp/new_index_path',
            'media_chunk_size': '1048576',
            'thumb_chunk_size': '524288'
        }
        self.config.load_config(config)
        self.assertEqual(self.config.media_path, '/tmp/new_media_path')
        self.assertEqual(self.config.index_path, '/tmp/new_index_path')
        self.assertEqual(self.config.media_chunk_size, 1048576)
        self.assertEqual(self.config.thumb_chunk_size, 524288)

    def test_validate_config_method(self):
        self.assertFalse(self.config.validate_config())

        # Creating media_path and index_path directories
        os.mkdir(self.config.media_path)
        os.mkdir(self.config.index_path)

        self.assertTrue(self.config.validate_config())

    def tearDown(self):
        if os.path.exists(self.config.media_path):
            os.rmdir(self.config.media_path)
        if os.path.exists(self.config.index_path):
            os.rmdir(self.config.index_path)