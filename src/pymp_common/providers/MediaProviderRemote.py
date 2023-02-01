import logging
import traceback
import requests
from typing import IO
from typing import Dict
from typing import List
from typing import Union

from pymp_common.dataaccess.http_request_factory import media_request_factory
from pymp_common.dataaccess.redis import media_service_da
from pymp_common.abstractions.providers import MediaProvider
from pymp_common.abstractions.providers import MediaChunk


class MediaProviderRemote(MediaProvider):
    def __init__(self, serviceId: str):
        self.serviceinfo = media_service_da.hget(serviceId)
        self.media_service_url = self.service_url()

    def __repr__(self) -> str:
        return f"MediaProviderRemote({self.media_service_url})"

    def service_url(self) -> Union[None, str]:
        if self.serviceinfo:
            scheme = self.serviceinfo["scheme"]
            host = self.serviceinfo["host"]
            port = self.serviceinfo["port"]
            return f"{scheme}://{host}:{port}"
        return None

    def loginfo(self, message):
        logging.info(f"{self.__repr__}{message}")

    def get_status(self) -> bool:
        if self.serviceinfo:
            scheme = self.serviceinfo["scheme"]
            host = self.serviceinfo["host"]
            port = self.serviceinfo["port"]
            return not scheme == "" and not host == "" and not port == ""
        return False

    def get_media_uri(self, mediaId: str) -> Union[str, None]:
        self.loginfo("get_media_uri")
        if self.media_service_url:
            apiRequest = media_request_factory._get_media_(
                self.media_service_url, mediaId, 0, None)
            return apiRequest.url
        return None

    def get_media_ids(self) -> List[str]:
        self.loginfo("get_media_ids")
        mediaIds = []
        session = requests.Session()
        apiRequest = media_request_factory._get_media_list_(
            self.media_service_url)
        apiResponse = session.send(apiRequest.prepare())
        self.loginfo(apiResponse.status_code)
        self.loginfo(apiResponse.content)
        for mediaId in apiResponse.json():
            mediaIds.append(mediaId)
        self.loginfo(mediaIds)
        return mediaIds

    def get_media_chunk(self, mediaId, sByte: int = 0, eByte: int = 0, fileSize: int = 0) -> Union[MediaChunk, None]:
        if not self.media_service_url is None:
            apiRequest = media_request_factory._get_media_(
                self.media_service_url, mediaId, sByte, eByte)

            session = requests.Session()

            logging.info(apiRequest)
            apiResponse = session.send(apiRequest.prepare())
            logging.info(apiResponse.headers)
            logging.info(apiResponse.status_code)

            if not apiResponse.headers.__contains__("content-range"):
                raise Exception("MISSING CONTENT RANGE")
            if not apiResponse.status_code == 206:
                # TODO HANDLER
                return None

            sByte, eByte, fileSize = MediaChunk.parse_range_header(
                apiResponse.headers["content-range"])
            return MediaChunk(apiResponse.content, sByte, eByte, fileSize)

        return None

    def save_media(self, name: str, stream: IO[bytes]):
        if not self.media_service_url is None:
            apiRequest = media_request_factory._post_media_(
                self.media_service_url, stream)
            session = requests.Session()
            session.send(apiRequest.prepare())

    def update_index(self):
        pass