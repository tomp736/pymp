import logging
from typing import List
from pymp_core.dto.media_info import MediaInfo
from pymp_core.providers import FfmpegProviderFactory, MediaProviderFactory
from pymp_core.utils.RepeatTimer import RepeatTimer
from pymp_core.app.config import PympServerRoles, ServerConfig
from pymp_core.dataaccess.redis import redis_media_process_queue
from pymp_core.decorators import prom

class FfmpegService:    
    def __init__(self, server_config: ServerConfig):
        self.server_config = server_config
        self.timer = RepeatTimer(60, self.process_media_services)

    def __repr__(self) -> str:
        return "FfmpegService()"

    def watch_media(self):
        self.timer.start()

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def process_media_services(self):
        if self.server_config.roles & PympServerRoles.FFMPEG_SVC:
            media_infos = redis_media_process_queue.rpop()
            while media_infos:
                for media_info in media_infos:
                    self.process_media_service(media_info)
                media_infos = redis_media_process_queue.rpop()

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def process_media_service(self, media_info: MediaInfo):
        self.process_media_thumb(media_info)
        self.process_media_meta(media_info)

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def process_media_thumb(self, media_info: MediaInfo):
        thumb_provider = MediaProviderFactory.get_thumb_providers()[0]
        if not thumb_provider.has_thumb(media_info.media_id):
            try:
                media_provider = MediaProviderFactory.get_data_providers(media_info.server_id)[
                    0]
                ffmpeg_provider = FfmpegProviderFactory.get_ffmpeg_providers()[0]
                thumb = ffmpeg_provider.get_thumb(
                    media_provider.get_media_uri(media_info.media_id))
                if thumb:
                    thumb_provider.set_thumb(media_info.media_id, thumb)
            except Exception as ex:
                logging.info(ex)

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def process_media_meta(self, media_info: MediaInfo):
        meta_provider = MediaProviderFactory.get_meta_providers()[0]
        if not meta_provider.has_meta(media_info.media_id):
            try:
                media_provider = MediaProviderFactory.get_data_providers(media_info.server_id)[
                    0]
                ffmpeg_provider = FfmpegProviderFactory.get_ffmpeg_providers()[0]
                meta = ffmpeg_provider.get_meta(
                    media_provider.get_media_uri(media_info.media_id))
                if meta:
                    meta_provider.set_meta(media_info.media_id, meta)
            except Exception as ex:
                logging.info(ex)
