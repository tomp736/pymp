import logging
import os
import uuid
from typing import IO
from typing import Dict
from typing import List
from typing import Union

from pymp_core.app.config import MediaConfig
from pymp_core.abstractions.providers import MediaDataProvider
from pymp_core.abstractions.providers import MediaChunk
from pymp_core.decorators import prom



class MediaFileDataProvider(MediaDataProvider):
    
    def __init__(self, media_config: MediaConfig):
        self.media_config = media_config
        self.status = True
        os.makedirs(self.media_config.media_path, exist_ok=True)
        os.makedirs(self.media_config.index_path, exist_ok=True)

    def __repr__(self) -> str:
        return f"MediaFileDataProvider({self.status})"

    def is_ready(self) -> bool:
        return self.status

    def is_readonly(self) -> bool:
        return False

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def get_media_uri(self, media_id: str) -> Union[str, None]:
        return os.path.join(self.media_config.index_path, media_id)

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def get_media_ids(self) -> List[str]:
        media_ids = []
        for media_id in self.read_indexfiles():
            media_ids.append(os.path.basename(media_id))
        return media_ids

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def get_media_chunk(self, media_id, start_byte=0, end_byte=None) -> Union[MediaChunk, None]:
        mediafile = self.get_media_uri(media_id)
        if not mediafile:
            logging.info("mediafile None")
            raise OSError(f"uri None")

        logging.info(mediafile)
        if not os.path.exists(mediafile):
            raise OSError(f"no such file: {mediafile}")

        file_size = os.stat(mediafile).st_size

        start, length = self.get_chunk_info(start_byte, end_byte, file_size)
        with open(mediafile, 'rb') as f:
            f.seek(start)
            chunk = f.read(length)

        return MediaChunk(chunk, start, start + length - 1, file_size)

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def save_media(self, name: str, stream: IO[bytes]):
        fullpath = os.path.join(self.media_config.media_path, name)

        with open(fullpath, "bw") as f:
            chunk_size = 4096
            while True:
                chunk = stream.read(chunk_size)
                if len(chunk) == 0:
                    return
                f.write(chunk)

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def read_index(self) -> Dict[str, str]:
        fs_indexfiles = self.read_indexfiles()
        index = {}

        for indexfile in fs_indexfiles:
            if os.path.islink(indexfile):
                mediafile = os.path.realpath(indexfile)
                media_id = os.path.basename(indexfile)
                index[media_id] = mediafile

        return index

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def update_index(self):
        fs_indexfiles = self.read_indexfiles()
        fs_mediafiles = self.read_mediafiles()

        logging.info(fs_indexfiles)
        logging.info(fs_mediafiles)

        for fs_indexfile in fs_indexfiles:
            islink = os.path.islink(fs_indexfile)
            exists = os.path.exists(fs_indexfile)
            if islink and exists:
                realpath = os.path.realpath(fs_indexfile)
                index_basename = os.path.basename(fs_indexfile)
                media_basename = os.path.basename(realpath)

                logging.info(realpath)
                if realpath in fs_mediafiles:
                    logging.info(f" -- INDEX OK -- : {realpath}")
                    fs_mediafiles.remove(realpath)
            else:
                os.remove(fs_indexfile)

        for fs_mediafile in fs_mediafiles:
            index_basename = str(uuid.uuid4())
            media_basename = os.path.basename(fs_mediafile)
            logging.info(f" -- ADDING -- {index_basename} = {media_basename}")
            os.symlink(f"../media/{media_basename}",
                       f"{self.media_config.index_path}/{index_basename}")

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def read_mediafiles(self):
        file_list = []
        for filename in os.listdir(self.media_config.media_path):
            filepath = os.path.join(self.media_config.media_path, filename)
            if os.path.isfile(filepath):
                file_list.append(filepath)
        return file_list

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def read_indexfiles(self):
        file_list = []
        for filename in os.listdir(self.media_config.index_path):
            filepath = os.path.join(self.media_config.index_path, filename)
            if os.path.isfile(filepath):
                file_list.append(filepath)
        return file_list

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def get_chunk_info(self, sByte: int = 0, eByte: int = 0, file_size: int = 0):
        start = 0
        if sByte < file_size:
            start = sByte

        length = file_size - sByte
        if eByte:
            length = eByte + 1 - sByte

        if length > self.media_config.media_chunk_size:
            length = self.media_config.media_chunk_size

        return start, length
