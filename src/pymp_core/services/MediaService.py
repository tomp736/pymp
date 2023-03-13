import logging
from typing import IO, List
from typing import Union
import io

from pymp_core.app.config import PympServerRoles, ServerConfig

from pymp_core.abstractions.providers import MediaChunk
from pymp_core.abstractions.providers import MediaDataProvider
from pymp_core.dto.service_info import ServiceInfo
from pymp_core.providers import MediaProviderFactory, MediaRegistryProviderFactory

from pymp_core.utils.RepeatTimer import RepeatTimer

from pymp_core.decorators import prom

class MediaService:
    
    def __init__(self, server_config: ServerConfig):
        self.server_config = server_config
        self.register_timer = RepeatTimer(60, self.register)

    def __repr__(self) -> str:
        return "MediaService()"

    def get_media_provider(self, media_id) -> Union[MediaDataProvider, None]:
        media_registry_providers = MediaRegistryProviderFactory.get_media_registry_providers()
        media_registry_provider = media_registry_providers[0]
        media_info = media_registry_provider.get_media_info(media_id)
        if media_info:
            for media_provider in MediaProviderFactory.get_data_providers(media_info.server_id):
                logging.info(media_provider)
                if (media_id in media_provider.get_media_ids()):
                    return media_provider

        return None

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def get_media_chunk(self, media_id, start_byte: int = 0, end_byte: int = 0) -> Union[MediaChunk, None]:
        media_provider = self.get_media_provider(media_id)
        if media_provider:
            return media_provider.get_media_chunk(media_id, start_byte, end_byte)
        return None

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def get_media_thumb(self, media_id) -> Union[io.BytesIO, None]:
        return MediaProviderFactory.get_thumb_providers()[0].get_thumb(media_id)

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def get_media_meta(self, media_id) -> Union[str, None]:
        return MediaProviderFactory.get_meta_providers()[0].get_meta(media_id)

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def save_media(self, name: str, stream: IO[bytes]):        
        media_provider = MediaProviderFactory.get_data_providers("")[0]
        if media_provider:
            return media_provider.save_media(name, stream)

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def get_media_ids(self) -> List[str]:
        if self.server_config.roles & PympServerRoles.MEDIA_SVC:
            media_provider = MediaProviderFactory.get_data_providers(self.server_config.id)[0]
            return media_provider.get_media_ids()
        return []

    def watch_media(self):
        self.register_timer.start()

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def update_index(self) -> None:
        if self.server_config.roles & PympServerRoles.MEDIA_SVC:
            media_provider = MediaProviderFactory.get_data_providers(self.server_config.id)[0]
            media_provider.update_index()

    def register(self) -> ServiceInfo:
        service_info = ServiceInfo(**self.server_config.__dict__)
        if self.server_config.roles & PympServerRoles.MEDIA_SVC:
            self.update_index()
            media_registry_providers = MediaRegistryProviderFactory.get_media_registry_providers(True)
            if len(media_registry_providers) == 0:
                raise Exception("No media registry providers available")
            
            media_registry_provider = media_registry_providers[0]
            logging.info(media_registry_provider.__repr__())
            registered_service_info = media_registry_provider.set_service_info(service_info)
            return registered_service_info
        return service_info
