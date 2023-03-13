
import logging
from typing import IO
from typing import List
from typing import Union

import requests
from pymp_core.app.config import ServiceConfig
from pymp_core.decorators import prom


from pymp_core.dataaccess.http_request_factory import http_request_factory
from pymp_core.abstractions.providers import MediaDataProvider
from pymp_core.abstractions.providers import MediaChunk


class MediaHttpDataProvider(MediaDataProvider):
    
    def __init__(self, service_config: ServiceConfig):
        self.status = True
        self.service_config = service_config
        self.readonly = False

    def __repr__(self) -> str:
        return f"MediaHttpDataProvider({self.get_service_url()})"

    def is_readonly(self) -> bool:
        return self.readonly

    def get_service_url(self) -> str:
        return self.service_config.get_uri()

    def is_ready(self) -> bool:
        return self.status

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def get_media_uri(self, media_id: str) -> str:
        media_request = http_request_factory.get(
            self.get_service_url(), f"/media/{media_id}")
        return media_request.url

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def get_media_ids(self) -> List[str]:
        media_ids = []
        session = requests.Session()
        media_request = http_request_factory.get(
            self.get_service_url(), "/media/list")
        media_response = session.send(media_request.prepare())
        logging.info(media_response.json())
        for media_id in media_response.json():
            media_ids.append(media_id)
        return media_ids

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def get_media_chunk(self, media_id, start_byte=0, end_byte=None) -> Union[MediaChunk, None]:
        media_request = http_request_factory.get(
            self.get_service_url(),
            f"/media/{media_id}",
            {
                'Range': f'bytes {start_byte}-{end_byte}'
            })
        session = requests.Session()
        media_response = session.send(media_request.prepare())
        if not "content-range" in media_response.headers:
            raise Exception("MISSING CONTENT RANGE")
        if not media_response.status_code == 206:
            # TODO HANDLER
            return None

        response_start_byte, response_end_byte, response_file_size = MediaChunk.parse_range_header(
            media_response.headers["content-range"])
        return MediaChunk(media_response.content, response_start_byte, response_end_byte, response_file_size)

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def save_media(self, name: str, stream: IO[bytes]):
        media_request = http_request_factory.post_data(
            self.get_service_url(), "/media", stream)
        session = requests.Session()
        session.send(media_request.prepare())

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def update_index(self):
        pass
