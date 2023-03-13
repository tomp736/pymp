import logging
from typing import List

from pymp_core.abstractions.providers import DataProvider, MediaDataProvider, MediaMetaProvider, MediaThumbProvider
from pymp_core.app.config import PympServerRoles, ServiceConfig
from pymp_core.app.config_factory import CONFIG_FACTORY, ConfigFactory
from pymp_core.providers import MediaRegistryProviderFactory
from pymp_core.providers.MetaRedisDataProvider import MetaRedisDataProvider
from pymp_core.providers.ThumbRedisDataProvider import ThumbRedisDataProvider
from pymp_core.providers.MediaFileDataProvider import MediaFileDataProvider
from pymp_core.providers.MediaHttpDataProvider import MediaHttpDataProvider


def get_data_providers(service_id: str, wants_write_access: bool = False) -> List[MediaDataProvider]:
    logging.info("GETTING MEDIA DATA PROVIDERS")
    media_providers = []

    # configure self
    server_config = CONFIG_FACTORY.get_server_config()    
    if server_config.roles & PympServerRoles.MEDIA_SVC:
        media_config = CONFIG_FACTORY.get_media_config()    
        media_file_data_provider = MediaFileDataProvider(media_config)
        if media_file_data_provider.check_data_provider(wants_write_access):
            media_providers.append(media_file_data_provider)

    # add hardcoded services
    service_configs = CONFIG_FACTORY.get_service_configs()  
    for service_config in service_configs:
        if service_config.roles & PympServerRoles.MEDIA_SVC:    
            if service_config.is_valid() and service_config.id == service_id:
                media_http_data_provider = MediaHttpDataProvider(service_config)
                if media_http_data_provider.check_data_provider(wants_write_access):
                    media_providers.append(media_http_data_provider)
                    
    # add data provider from media_registry
    if not server_config.roles & PympServerRoles.MEDIA_SVC:
        media_registry_provider = MediaRegistryProviderFactory.get_media_registry_providers()[0]
        if media_registry_provider:
            service_info = media_registry_provider.get_service_info(service_id)
            service_config = ServiceConfig(**service_info.__dict__)
            if service_info and service_config and service_config.is_valid():
                media_provider = MediaHttpDataProvider(service_config)
                if media_provider.check_data_provider(wants_write_access):
                    media_providers.append(media_provider)

    return media_providers

def get_thumb_providers(wants_write_access: bool = False) -> List[MediaThumbProvider]:
    logging.info("GETTING MEDIA THUMB PROVIDERS")
    thumb_providers = []

    thumb_provider = ThumbRedisDataProvider()
    if thumb_provider.check_data_provider(wants_write_access):
        thumb_providers.append(thumb_provider)

    return thumb_providers

def get_meta_providers(wants_write_access: bool = False) -> List[MediaMetaProvider]:
    logging.info("GETTING MEDIA META PROVIDERS")
    meta_providers = []

    meta_provider = MetaRedisDataProvider()
    if meta_provider.check_data_provider(wants_write_access):
        meta_providers.append(meta_provider)

    return meta_providers
