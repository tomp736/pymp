import logging
import os
import traceback
import uuid
from typing import IO
from typing import Dict
from typing import List
from typing import Union

from pymp_common.app.PympConfig import pymp_env
from pymp_common.abstractions.providers import MediaProvider
from pymp_common.abstractions.providers import MediaChunk


class MediaProviderLocal(MediaProvider):
    def __init__(self):
        self.mediapath = pymp_env.get("MEDIA_SVC_MEDIAPATH")
        self.indexpath = pymp_env.get("MEDIA_SVC_INDEXPATH")
        if not os.path.exists(self.mediapath):
            os.mkdir(self.mediapath)
        if not os.path.exists(self.indexpath):
            os.mkdir(self.indexpath)
        
    def __repr__(self) -> str:
        return f"MediaProviderLocal({self.mediapath})"

    def loginfo(self, message):
        logging.info(f"{self.__repr__()}{message}")

    def get_status(self) -> bool:
        return True

    def get_media_uri(self, media_id: str) -> Union[str, None]:
        return os.path.join(self.indexpath, media_id)

    def get_media_ids(self) -> List[str]:
        ids = []
        for id in self.read_indexfiles():
            ids.append(os.path.basename(id))
        return ids

    def save_media(self, name: str, stream: IO[bytes]):
        fullpath = os.path.join(self.mediapath, name)

        with open(fullpath, "bw") as f:
            chunk_size = 4096
            while True:
                chunk = stream.read(chunk_size)
                if len(chunk) == 0:
                    return
                f.write(chunk)

    def get_media_chunk(self, mediaId, sByte: int = 0, eByte: int = 0, fileSize: int = 0) -> Union[MediaChunk, None]:
        mediafile = self.get_media_uri(mediaId)
        if not mediafile:
            logging.info("mediafile None")
            raise OSError(f"uri None")

        logging.info(mediafile)
        if not os.path.exists(mediafile):
            raise OSError(f"no such file: {mediafile}")

        if fileSize == 0:
            fileSize = os.stat(mediafile).st_size

        start, length = self.get_chunk_info(sByte, eByte, fileSize)
        with open(mediafile, 'rb') as f:
            f.seek(start)
            chunk = f.read(length)

        return MediaChunk(chunk, start, start + length - 1, fileSize)

    def read_index(self) -> Dict[str, str]:
        fs_indexfiles = self.read_indexfiles()
        index = {}

        for indexfile in fs_indexfiles:
            if os.path.islink(indexfile):
                mediafile = os.path.realpath(indexfile)
                id = os.path.basename(indexfile)
                index[id] = mediafile

        return index

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
                if (fs_mediafiles.__contains__(realpath)):
                    logging.info(f" -- INDEX OK -- : {realpath}")
                    fs_mediafiles.remove(realpath)
            else:
                os.remove(fs_indexfile)

        for fs_mediafile in fs_mediafiles:
            index_basename = str(uuid.uuid4())
            media_basename = os.path.basename(fs_mediafile)
            logging.info(f" -- ADDING -- {index_basename} = {media_basename}")
            os.symlink(f"../media/{media_basename}",
                       f"{self.indexpath}/{index_basename}")

    def read_mediafiles(self):
        file_list = []
        for filename in os.listdir(self.mediapath):
            filepath = os.path.join(self.mediapath, filename)
            if os.path.isfile(filepath):
                file_list.append(filepath)
        return file_list

    def read_indexfiles(self):
        file_list = []
        for filename in os.listdir(self.indexpath):
            filepath = os.path.join(self.indexpath, filename)
            if os.path.isfile(filepath):
                file_list.append(filepath)
        return file_list

    def get_chunk_info(self, sByte: int = 0, eByte: int = 0, file_size: int = 0):
        start = 0
        if sByte < file_size:
            start = sByte

        length = file_size - sByte
        if eByte:
            length = eByte + 1 - sByte

        if length > int(pymp_env.get("MEDIA_CHUNK_SIZE")):
            length = int(pymp_env.get("MEDIA_CHUNK_SIZE"))

        return start, length
