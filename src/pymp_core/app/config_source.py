

from abc import abstractmethod
import json
import os
from typing import Dict, List

from pymp_core.app.config import ServiceConfig


class IConfigSource:

    @property
    @abstractmethod
    def can_write(self) -> bool:
        pass

    @property
    @abstractmethod
    def can_read(self) -> bool:
        pass

    @abstractmethod
    def get_values(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def set_value(self, key, value) -> bool:
        pass


class EnvironmentConfigSource(IConfigSource):

    @property
    def can_write(self) -> bool:
        return False

    @property
    def can_read(self) -> bool:
        return True

    def get_values(self) -> Dict[str, str]:
        if self.can_read:
            return {key: value for key, value in os.environ.items()}
        return {}

    def set_value(self, key, value):
        return False


class RuntimeConfigSource(IConfigSource):

    _runtime_config: Dict[str, str] = {}

    @property
    def can_write(self) -> bool:
        return True

    @property
    def can_read(self) -> bool:
        return True

    def get_values(self) -> Dict[str, str]:
        if self.can_read:
            return {key: value for key, value in self._runtime_config.items()}
        return {}

    def set_value(self, key, value):
        if self.can_write:
            self._runtime_config[key] = value
            return True
        return False


class JsonServiceConfigReader:
    def __init__(self, config_file_path: str) -> None:
        self.config_file_path = config_file_path
        self.exists = os.path.exists(self.config_file_path)

    def load_config(self) -> List[ServiceConfig]:
        if self.exists:
            with open(self.config_file_path, 'r', encoding='utf-8') as file_io:
                data = json.load(file_io)
            return [ServiceConfig(**config) for config in data]
        return []
