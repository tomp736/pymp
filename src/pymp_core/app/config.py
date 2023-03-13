from abc import abstractmethod
from enum import IntFlag
from typing import Dict
import os
import logging

class PympServerRoles(IntFlag):
    NONE = 1
    MEDIA_API = 2
    META_API = 4
    THUMB_API = 8
    MEDIA_SVC = 16
    FFMPEG_SVC = 32
    MEDIAREGISTRY_SVC = 64


class IConfig():

    @abstractmethod
    def load(self, kwargs):
        pass

    @abstractmethod
    def load_config(self, config: Dict[str, str]):
        pass

    @abstractmethod
    def validate_config(self) -> bool: 
        pass


class FlaskConfig(IConfig):

    host: str = ""
    port: int = 80
    cors_headers: str = "*"

    def __init__(self, **kwargs) -> None:
        self.load(kwargs)

    def load(self, kwargs):
        self.host = kwargs.get('host', self.host)
        self.port = kwargs.get('port', self.port)
        self.cors_headers = kwargs.get('cors_headers', self.cors_headers)

    def load_config(self, config: Dict[str, str]):
        self.host = config.get('host', self.host)
        self.port = int(config.get('port', self.port))
        self.cors_headers = config.get('cors_headers', self.cors_headers)

    def validate_config(self) -> bool:
        return True


class ServerConfig(IConfig):

    id: str = ""
    roles: PympServerRoles = PympServerRoles.NONE
    host: str = ""
    proto: str = "http"
    port: int = 80

    def __init__(self, **kwargs) -> None:
        self.load(kwargs)

    def load(self, kwargs):
        self.id = kwargs.get('id', self.id)
        self.roles = kwargs.get('roles', self.roles)
        self.proto = kwargs.get('proto', self.proto)
        self.host = kwargs.get('host', self.host)
        self.port = kwargs.get('port', self.port)

    def load_config(self, config: Dict[str, str]):
        self.id = config.get('id', self.id)
        self.roles = PympServerRoles(int(config.get('roles', self.roles)))
        self.proto = config.get('proto', self.proto)
        self.host = config.get('host', self.host)
        self.port = int(config.get('port', self.port))

    def validate_config(self) -> bool:
        return True

class ServiceConfig(IConfig):

    id: str = ""
    roles: PympServerRoles = PympServerRoles.NONE
    host: str = ""
    proto: str = "http"
    port: int = 80

    def __init__(self, **kwargs) -> None:
        self.load(kwargs)

    def load(self, kwargs):
        logging.info(kwargs)
        self.id = kwargs.get('id', self.id)
        self.roles = kwargs.get('roles', self.roles)
        self.proto = kwargs.get('proto', self.proto)
        self.host = kwargs.get('host', self.host)
        self.port = kwargs.get('port', self.port)

    def load_config(self, config: Dict[str, str]):
        logging.info(config)
        self.id = config.get('id', self.id)
        self.roles = PympServerRoles(int(config.get('roles', self.roles)))
        self.proto = config.get('proto', self.proto)
        self.host = config.get('host', self.host)
        self.port = int(config.get('port', self.port))

    def validate_config(self) -> bool:
        if self.proto in ["http", "https"]:
            return True
        else:
            return False

    def get_uri(self):
        if self.validate_config():
            return f"{self.proto}://{self.host}:{self.port}"
        else:
            raise Exception(f"ServiceInfo Not Valid: {self.__dict__}")


class RedisConfig(IConfig):

    host: str = ""
    port: int = 2379

    def __init__(self, **kwargs) -> None:
        self.load(kwargs)

    def load(self, kwargs):
        self.host = kwargs.get('host', self.host)
        self.port = kwargs.get('port', self.port)

    def load_config(self, config: Dict[str, str]):
        self.host = config.get('host', self.host)
        self.port = int(config.get('port', self.port))

    def validate_config(self) -> bool:
        return True

class MediaConfig(IConfig):

    media_path: str = ""
    index_path: str = ""
    media_chunk_size: int = 2 ** 22
    thumb_chunk_size: int = 2 ** 20

    def __init__(self, **kwargs) -> None:
        self.load(kwargs)

    def load(self, kwargs):
        logging.info(kwargs)
        self.media_path = kwargs.get('media_path', self.media_path)
        self.index_path = kwargs.get('index_path', self.index_path)
        self.media_chunk_size = int(kwargs.get(
            'media_chunk_size', self.media_chunk_size))
        self.thumb_chunk_size = int(kwargs.get(
            'thumb_chunk_size', self.thumb_chunk_size))

    def load_config(self, config: Dict[str, str]):
        logging.info(config)
        self.media_path = config.get('media_path', self.media_path)
        self.index_path = config.get('index_path', self.index_path)
        self.media_chunk_size = int(config.get(
            'media_chunk_size', self.media_chunk_size))
        self.thumb_chunk_size = int(config.get(
            'thumb_chunk_size', self.thumb_chunk_size))

    def validate_config(self) -> bool:
        logging.info(self.__dict__)
        if not os.path.exists(self.media_path):
            return False
        if not os.path.exists(self.index_path):
            return False
        return True

