import logging

from pymp_core.app.config import PympServerRoles, ServerConfig

from pymp_core.dto.media_info import MediaInfo
from pymp_core.dto.service_info import ServiceInfo
from pymp_core.dataaccess.redis import redis_media_process_queue

from pymp_core.providers import MediaProviderFactory, MediaRegistryProviderFactory

from pymp_core.utils.RepeatTimer import RepeatTimer

from pymp_core.decorators import prom

class MediaRegistryService():
    
    def __init__(self, server_config: ServerConfig):
        self.server_config = server_config
        self.timer = RepeatTimer(60, self.update_media_services)

    def __repr__(self) -> str:
        return "MediaRegistryService()"

    def get_media_registry_provider(self):
        media_registry_provider = MediaRegistryProviderFactory.get_media_registry_providers()[
            0]
        return media_registry_provider

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def register_service(self, service_info: ServiceInfo) -> ServiceInfo:
        media_registry_provider = self.get_media_registry_provider()
        return media_registry_provider.set_service_info(service_info)

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def register_media(self, media_info: MediaInfo):
        media_registry_provider = self.get_media_registry_provider()
        return media_registry_provider.set_media_info(media_info)

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def get_media_info(self, media_id) -> MediaInfo:
        media_registry_provider = self.get_media_registry_provider()
        return media_registry_provider.get_media_info(media_id)

    def watch_services(self):
        self.timer.start()

    def update_media_services(self):
        media_registry_provider = self.get_media_registry_provider()
        if not self.server_config.roles & PympServerRoles.MEDIAREGISTRY_SVC:
            return

        media_service = media_registry_provider.get_all_service_info()
        if not media_service:
            return

        for media_server_id in media_service:
            media_svc_media_ids = self.check_media_service(media_server_id)
            self.check_media_info(media_server_id, media_svc_media_ids)
            
        self.check_hanging_media()

    def check_media_service(self, server_id):
        self.logstuff(f"CHECKING SERVICE FOR {server_id}")
        media_svc_media_ids = []
        media_registry_provider = self.get_media_registry_provider()
        try:
            media_provider = MediaProviderFactory.get_data_providers(server_id)[
                0]
            if media_provider and media_provider.is_ready():
                logging.info(media_provider)
                media_svc_media_ids = media_provider.get_media_ids()
                self.logstuff(f"{media_provider} registered.")
            else:
                self.logstuff(f"{media_provider} is not ready.")
                media_registry_provider.del_service_info(server_id)
        except Exception as ex:
            media_registry_provider.del_service_info(server_id)
            logging.info(ex)
        return media_svc_media_ids

    def check_media_info(self, server_id, service_media_ids):
        self.logstuff(f"CHECKING SOURCES FOR {server_id}")
        self.logstuff(f"{server_id} REPORTED {service_media_ids}")

        media_registry_provider = self.get_media_registry_provider()
        registry_media = media_registry_provider.get_all_media_info()
        if registry_media is None:
            self.logstuff("registry_media is NONE")
            return

        redis_svc_media_ids = []
        for registry_media_id in registry_media:
            if registry_media[registry_media_id].server_id == server_id:
                redis_svc_media_ids.append(registry_media_id)

        for registry_media_id in redis_svc_media_ids:
            # delete from redis if media_svc no longer has the media
            if registry_media_id not in service_media_ids:
                self.logstuff(f"DELETING: {registry_media_id}")
                media_registry_provider.del_media_info(registry_media_id)
                continue

            # if media source for media  has changed, update redis
            if registry_media[registry_media_id].server_id != server_id:
                self.logstuff(f"UPDATING: {registry_media_id}")
                media_info = MediaInfo()
                media_info.media_id = registry_media_id
                media_info.server_id = server_id
                media_registry_provider.set_media_info(media_info)
                continue

        # Queue for processing if needed
        thumb_provider = MediaProviderFactory.get_thumb_providers()[0]
        meta_provider = MediaProviderFactory.get_meta_providers()[0]
        for media_id in service_media_ids:
            self.logstuff(f"UPDATING: {media_id}")
            media_info = MediaInfo()
            media_info.media_id = media_id
            media_info.server_id = server_id
            media_registry_provider.set_media_info(media_info)
            if not thumb_provider.has_thumb(media_id) or not meta_provider.has_meta(media_id):
                redis_media_process_queue.lpush(media_info)

    def check_hanging_media(self):
        self.logstuff(f"CHECKING HANGING MEDIA")

        media_registry_provider = self.get_media_registry_provider()
        registry_media_infos = media_registry_provider.get_all_media_info()
        registry_service_infos = media_registry_provider.get_all_service_info()
        
        server_ids = [service_info.id for _, service_info in registry_service_infos.items()]

        hanging_media_ids = []
        for registry_media_id in registry_media_infos:
            if registry_media_infos[registry_media_id].server_id not in server_ids:
                hanging_media_ids.append(registry_media_id)

        for registry_media_id in hanging_media_ids:
            self.logstuff(f"DELETING: {registry_media_id}")
            media_registry_provider.del_media_info(registry_media_id)
            continue

    def logstuff(self, message):
        logging.info(f"MEDIASERVICE: {message}")
