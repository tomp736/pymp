
import json
import logging
from typing import Dict
from typing import Union
import requests
from pymp_core.abstractions.providers import MediaRegistryDataProvider
from pymp_core.app.config import ServiceConfig

from pymp_core.dataaccess.http_request_factory import http_request_factory
from pymp_core.decorators import prom
from pymp_core.dto.media_info import MediaInfo
from pymp_core.dto.service_info import ServiceInfo


class MediaRegistryHttpDataProvider(MediaRegistryDataProvider):
    
    def __init__(self, service_config: ServiceConfig):
        self.service_config = service_config
        self.status = True
        self.readonly = False

    def __repr__(self) -> str:
        readonly = self.is_readonly()
        ready = self.is_readonly()
        return f"MediaRegistryHttpDataProvider({readonly},{ready})"

    def is_readonly(self) -> bool:
        return self.readonly

    def get_service_url(self) -> str:
        return self.service_config.get_uri()

    def is_ready(self) -> bool:
        return self.status

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def get_service_info(self, server_id: str) -> ServiceInfo:
        registry_request = http_request_factory.get(
            self.get_service_url(), f"/registry/service/{server_id}")
        session = requests.Session()
        registry_response = session.send(registry_request.prepare())
        response_json = registry_response.json()
        return ServiceInfo(**response_json)

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def get_all_service_info(self) -> Dict[str, ServiceInfo]:
        registry_request = http_request_factory.get(
            self.get_service_url(), "/registry/service")
        session = requests.Session()
        registry_response = session.send(registry_request.prepare())
        response_json = registry_response.json()
        return {server_id: ServiceInfo(**service_info) for server_id, service_info in response_json.items()}

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def set_service_info(self, service_info: ServiceInfo) -> ServiceInfo:
        logging.info(service_info)
        logging.info(service_info.to_json())
        registry_request = http_request_factory.post_json(
            self.get_service_url(), "/registry/service", service_info.to_json())
        session = requests.Session()
        response = session.send(registry_request.prepare())
        logging.info(response)
        response_json = response.json()
        return ServiceInfo(**response_json)

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def del_service_info(self, server_id: str) -> int:
        raise Exception("NOT IMPLEMENETED")

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def get_media_info(self, media_id: str) -> MediaInfo:
        registry_request = http_request_factory.get(
            self.get_service_url(), f"/registry/media/{media_id}")
        session = requests.Session()
        registry_response = session.send(registry_request.prepare())
        response_json = registry_response.json()
        return MediaInfo(**response_json)

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def get_all_media_info(self) -> Dict[str, MediaInfo]:
        registry_request = http_request_factory.get(
            self.get_service_url(), "/registry/media")
        session = requests.Session()
        registry_response = session.send(registry_request.prepare())
        response_json = registry_response.json()
        return {media_id: MediaInfo(**media_info) for media_id, media_info in response_json.items()}

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def set_media_info(self, media_info: MediaInfo) -> bool:
        registry_request = http_request_factory.post_json(
            self.get_service_url(), "/registry/media", media_info.to_json())
        session = requests.Session()
        registry_response = session.send(registry_request.prepare())
        return registry_response.json()

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def del_media_info(self, media_id: str) -> bool:
        raise Exception("NOT IMPLEMENETED")
