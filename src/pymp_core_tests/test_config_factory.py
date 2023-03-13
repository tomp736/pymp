import logging
import os
import unittest
from unittest.mock import MagicMock

from pymp_core.app.config import PympServerRoles
from pymp_core.app.config_factory import ConfigFactory
from pymp_core.app.config_source import EnvironmentConfigSource, RuntimeConfigSource


class ConfigFactoryTest(unittest.TestCase):
    def setUp(self):
        os.environ['SERVER_ID'] = 'test_server'
        os.environ['SERVER_ROLES'] = '30'
        os.environ['SERVER_HOST'] = 'test_host'
        os.environ['SERVER_PROTO'] = 'http'
        os.environ['SERVER_PORT'] = '8080'        

    def tearDown(self):
        del os.environ['SERVER_ID']
        del os.environ['SERVER_ROLES']
        del os.environ['SERVER_HOST']
        del os.environ['SERVER_PROTO']
        del os.environ['SERVER_PORT']
        
    def test_create_server_config(self):
        
        runtime_config_source = RuntimeConfigSource()
        environment_config_source = EnvironmentConfigSource()
        
        config_factory = ConfigFactory([environment_config_source, runtime_config_source], [])
        
        server_config = config_factory.get_server_config()
        self.assertEqual(server_config.roles, PympServerRoles.MEDIA_API | PympServerRoles.META_API | PympServerRoles.THUMB_API | PympServerRoles.MEDIA_SVC)
        
    def test_create_server_config_runtime_update_server_role(self):
        
        runtime_config_source = RuntimeConfigSource()
        environment_config_source = EnvironmentConfigSource()
        
        config_factory = ConfigFactory([environment_config_source, runtime_config_source], [])
        
        server_config = config_factory.get_server_config()
        self.assertEqual(server_config.roles, PympServerRoles.MEDIA_API | PympServerRoles.META_API | PympServerRoles.THUMB_API | PympServerRoles.MEDIA_SVC)
        
        runtime_config_source.set_value("SERVER_ROLES", PympServerRoles.NONE)
        
        server_config = config_factory.get_server_config()
        self.assertEqual(server_config.roles, PympServerRoles.NONE)
        
    def test_create_server_config_runtime_update_server_id(self):
                
        runtime_config_source = RuntimeConfigSource()
        environment_config_source = EnvironmentConfigSource()  
                
        config_factory = ConfigFactory([environment_config_source, runtime_config_source], [])
        
        server_config = config_factory.get_server_config()
        self.assertEqual(server_config.id, "test_server")
        
        runtime_config_source.set_value("SERVER_ID", "NEWID")
        
        server_config = config_factory.get_server_config()
        self.assertEqual(server_config.id, "NEWID")