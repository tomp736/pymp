

from typing import Dict, TypeVar
from pymp_core.app.config import FlaskConfig, IConfig, MediaConfig, RedisConfig, ServerConfig

from pymp_core.app.config_source import IConfigSource



class ConfigBuilder:
    
    CONFIG_TYPE = TypeVar('CONFIG_TYPE')

    def build(self, config_source: IConfigSource, config: CONFIG_TYPE) -> CONFIG_TYPE:
        if isinstance(config, IConfig):
            config_source_dict = config_source.get_values()
            config_dict: Dict[str, str] = {}
            if isinstance(config, ServerConfig):
                config_dict = {key.lower().replace('server_', '', 1): value for key,
                            value in config_source_dict.items() if key.startswith('SERVER_')}
            if isinstance(config, FlaskConfig):
                config_dict = {key.lower().replace('flask_', '', 1): value for key,
                            value in config_source_dict.items() if key.startswith('FLASK_')}
            if isinstance(config, RedisConfig):
                config_dict = {key.lower().replace('redis_', '', 1): value for key,
                            value in config_source_dict.items() if key.startswith('REDIS_')}
            if isinstance(config, MediaConfig):
                config_dict = {key.lower().replace('media_', '', 1): value for key,
                            value in config_source_dict.items() if key.startswith('MEDIA_')}
            config.load_config(config_dict)
        
        return config