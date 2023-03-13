from abc import ABC

import redis

from typing import Dict, List
from typing import Union
from pymp_core.app.config import RedisConfig

from pymp_core.app.config_factory import CONFIG_FACTORY
from pymp_core.dto.media_info import MediaInfo
from pymp_core.dto.service_info import ServiceInfo


class RedisDataAccess(ABC):
    def __init__(self, decode_responses):
        self.config = CONFIG_FACTORY.get_redis_config()
        self.redis = redis.Redis(host=self.config.host, port=self.config.port, db=0, decode_responses=decode_responses)

    def is_redis_readonly_replica(self) -> bool:
        info = self.redis.info()
        return info.get("role") == "slave" and info.get("master_link_status") == "up"


class RedisServiceInfoDataAccess(RedisDataAccess):
    def __init__(self):
        super().__init__(True)
        self.key = "media_service"

    def has(self) -> Union[bool, None]:
        return self.redis.exists(self.key) > 0

    def hhas(self, media_id: str) -> Union[bool, None]:
        return self.redis.hexists(self.key, media_id)

    def expire(self):
        if not self.is_redis_readonly_replica():
            self.redis.expire(self.key, 180)

    def hset(self, service_info: ServiceInfo):
        self.expire()
        return self.redis.hset(
            self.key,
            service_info.id,
            service_info.to_json()
        )

    def hget(self, service_id: str) -> Union[ServiceInfo, None]:
        service_info = self.redis.hget(self.key, service_id)
        if service_info is not None:
            return ServiceInfo.from_json(service_info)
        return None

    def hdel(self, media_id: str):
        return self.redis.hdel(f"{self.key}", media_id)

    def hgetall(self) -> Dict[str, ServiceInfo]:
        service_infos_json = self.redis.hgetall(self.key)
        service_infos = {
            server_id: ServiceInfo.from_json(service_info) for server_id, service_info in service_infos_json.items()
        }
        return service_infos


redis_service_info = RedisServiceInfoDataAccess()


class RedisMediaInfoDataAccess(RedisDataAccess):
    def __init__(self):
        super().__init__(True)
        self.key = f"media_info"

    def has(self) -> bool:
        return self.redis.exists(self.key) > 0

    def hhas(self, media_id: str) -> bool:
        return self.redis.hexists(self.key, media_id)

    def expire(self):
        if not self.is_redis_readonly_replica():
            self.redis.expire(self.key, 180)

    def hset(self, media_info: MediaInfo):
        return self.redis.hset(self.key, media_info.media_id, media_info.to_json())

    def hget(self, media_id: str) -> MediaInfo:
        return MediaInfo.from_json(self.redis.hget(self.key, media_id))

    def hdel(self, media_id: str):
        if not self.is_redis_readonly_replica():
            return self.redis.hdel(self.key, media_id)

    def hgetall(self) -> Dict[str, MediaInfo]:
        media_infos_json = self.redis.hgetall(self.key)
        media_infos = {media_id: MediaInfo.from_json(media_info_json) for media_id, media_info_json in media_infos_json.items()}
        return media_infos


redis_media_info = RedisMediaInfoDataAccess()


class RedisMedia(RedisDataAccess):
    def __init__(self, key):
        super().__init__(False)
        self.key = key

    def has(self, media_id: str) -> bool:
        return self.redis.exists(f"{self.key}_{media_id}") > 0

    def expire(self, media_id: str):
        if not self.is_redis_readonly_replica():
            self.redis.expire(f"{self.key}_{media_id}", 360)

    def set(self, media_id: str, value: bytes):
        return self.redis.set(f"{self.key}_{media_id}", value)

    def get(self, media_id: str) -> Union[bytes, None]:
        return self.redis.get(f"{self.key}_{media_id}")


class RedisMediaProcessQueue(RedisDataAccess):
    def __init__(self):
        super().__init__(True)
        self.key = "media_process_queue"
        
    def rpop(self, count = 10) -> List[MediaInfo]:
        media_infos_json = self.redis.rpop(self.key, count)
        if media_infos_json:
            media_infos = [MediaInfo.from_json(media_info_json) for media_info_json in media_infos_json]
            return media_infos
        return []
        
    def lpush(self, media_info: MediaInfo):
        self.redis.lpush(self.key, media_info.to_json())
        

redis_media_process_queue = RedisMediaProcessQueue()


class RedisMediaData(RedisMedia):
    def __init__(self):
        super().__init__("media_data")

redis_media_meta = RedisMediaData()


class RedisMediaMeta(RedisMedia):
    def __init__(self):
        super().__init__("media_meta")

redis_media_meta = RedisMediaMeta()


class RedisMediaThumb(RedisMedia):
    def __init__(self):
        super().__init__("media_thumb")


redis_media_thumb = RedisMediaThumb()
