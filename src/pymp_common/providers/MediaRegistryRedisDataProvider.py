
import json
import logging
from typing import Dict
from typing import Union
from pymp_common.abstractions.providers import MediaRegistryDataProvider

from pymp_common.dataaccess.redis import redis_service_info
from pymp_common.dataaccess.redis import redis_media_info
from pymp_common.decorators.prom import prom_count

from pymp_common.dto.MediaRegistry import MediaInfo, ServiceInfo


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

    @prom_count
    def get_service_info(self, service_id: str) -> Union[ServiceInfo, None]:
        return redis_service_info.hget(service_id)

    @prom_count
    def get_all_service_info(self) -> Dict[str, ServiceInfo]:
        return redis_service_info.hgetall()

    @prom_count
    def set_service_info(self, service_info: ServiceInfo) -> bool:
        redis_service_info.hset(service_info)
        return True

    @prom_count
    def del_service_info(self, service_id) -> Union[int, None]:
        return redis_service_info.hdel(service_id)

    # media_id -> MEDIAINFO

    @prom_count
    def get_media_info(self, media_id: str) -> MediaInfo:
        return redis_media_info.hget(media_id)

    @prom_count
    def get_all_media_info(self) -> Dict[str, MediaInfo]:
        return redis_media_info.hgetall()

    @prom_count
    def set_media_info(self, media_info: MediaInfo) -> bool:
        return redis_media_info.hset(media_info) > 0

    @prom_count
    def del_media_info(self, media_id: str) -> bool:
        return redis_media_info.hdel(media_id) > 0
