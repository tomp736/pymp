
import json
import logging
from typing import Dict
from typing import Union
from pymp_core.abstractions.providers import MediaRegistryDataProvider

from pymp_core.dataaccess.redis import redis_service_info
from pymp_core.dataaccess.redis import redis_media_info
from pymp_core.decorators import prom

from pymp_core.dto.media_info import MediaInfo
from pymp_core.dto.service_info import ServiceInfo


class MediaRegistryRedisDataProvider(MediaRegistryDataProvider):

    def __repr__(self) -> str:
        readonly = self.is_readonly()
        ready = self.is_ready()
        return f"MediaRegistryRedisDataProvider(ready:{ready},readonly:{readonly})"

    def is_readonly(self) -> bool:
        try:
            return redis_service_info.is_redis_readonly_replica()
        except Exception as err:
            logging.info(f"Unexpected {err=}, {type(err)=}")
            return True

    def is_ready(self) -> bool:
        try:
            return redis_service_info.redis.ping()
        except Exception as err:
            logging.info(f"Unexpected {err=}, {type(err)=}")
            return False

    # SERVICEID => SERVICEINFO

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def get_service_info(self, server_id: str) -> Union[ServiceInfo, None]:
        return redis_service_info.hget(server_id)

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def get_all_service_info(self) -> Dict[str, ServiceInfo]:
        return redis_service_info.hgetall()

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def set_service_info(self, service_info: ServiceInfo) -> ServiceInfo:
        redis_service_info.hset(service_info)
        return service_info

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def del_service_info(self, server_id) -> Union[int, None]:
        return redis_service_info.hdel(server_id)

    # media_id -> MEDIAINFO

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def get_media_info(self, media_id: str) -> MediaInfo:
        return redis_media_info.hget(media_id)

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def get_all_media_info(self) -> Dict[str, MediaInfo]:
        return redis_media_info.hgetall()

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def set_media_info(self, media_info: MediaInfo) -> bool:
        return redis_media_info.hset(media_info) > 0

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def del_media_info(self, media_id: str) -> bool:
        redis_media_info.hdel(media_id)
        return True
