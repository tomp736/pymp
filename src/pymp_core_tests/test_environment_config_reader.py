import os
import unittest

from pymp_core.app.config import FlaskConfig, MediaConfig, PympServerRoles, RedisConfig, ServerConfig
from pymp_core.app.config_source import EnvironmentConfigSource


class EnvironmentConfigSourceTest(unittest.TestCase):
    def setUp(self):
        os.environ['SERVER_ID'] = 'test_server'
        os.environ['SERVER_ROLES'] = '14'
        os.environ['SERVER_HOST'] = 'test_host'
        os.environ['SERVER_PROTO'] = 'https'
        os.environ['SERVER_PORT'] = '8080'

        os.environ['FLASK_HOST'] = '0.0.0.0'
        os.environ['FLASK_PORT'] = '80'
        os.environ['FLASK_CORS_HEADERS'] = '*'

        os.environ['REDIS_HOST'] = 'test_redis'
        os.environ['REDIS_PORT'] = '6379'

        os.environ['MEDIA_PATH'] = '/test/media'
        os.environ['INDEX_PATH'] = '/test/index'
        os.environ['MEDIA_CHUNK_SIZE'] = '2048'
        os.environ['THUMB_CHUNK_SIZE'] = '1024'

    def tearDown(self):
        del os.environ['SERVER_ID']
        del os.environ['SERVER_ROLES']
        del os.environ['SERVER_HOST']
        del os.environ['SERVER_PROTO']
        del os.environ['SERVER_PORT']

        del os.environ['FLASK_HOST']
        del os.environ['FLASK_PORT']
        del os.environ['FLASK_CORS_HEADERS']

        del os.environ['REDIS_HOST']
        del os.environ['REDIS_PORT']

        del os.environ['MEDIA_PATH']
        del os.environ['INDEX_PATH']
        del os.environ['MEDIA_CHUNK_SIZE']
        del os.environ['THUMB_CHUNK_SIZE']

    def test_load_server_config(self):
        reader = EnvironmentConfigSource()
        config = reader.get_values()

        self.assertEqual(config['SERVER_ID'], 'test_server')
        self.assertEqual(config['SERVER_ROLES'], str(int(PympServerRoles.MEDIA_API | PympServerRoles.META_API | PympServerRoles.THUMB_API)))
        self.assertEqual(config['SERVER_HOST'], 'test_host')
        self.assertEqual(config['SERVER_PROTO'], 'https')
        self.assertEqual(config['SERVER_PORT'], '8080')