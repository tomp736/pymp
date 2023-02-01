

from typing import Union
import io
from pymp_common.abstractions.providers import FfmpegProvider

from pymp_common.dataaccess.redis import media_thumb_da
from pymp_common.dataaccess.redis import media_meta_da

from pymp_common.app.PympConfig import pymp_env
from pymp_common.app.PympConfig import PympServer

class FfmpegProviderRedis(FfmpegProvider):
    def __init__(self) -> None:
        if pymp_env.get_servertype() & PympServer.FFMPEG_SVC:
            self.status = False
        else:
            self.status = True
        self.is_readonly = media_thumb_da.is_redis_readonly_replica()

    def __repr__(self) -> str:
        return "FfmpegProviderRedis()"
        
    def readonly(self) -> bool:
        return self.is_readonly
    
    def get_status(self) -> bool:
        return self.status
    
    def get_thumb(self, media_id) -> Union[io.BytesIO, None]:
        thumb = media_thumb_da.get(media_id)
        if thumb:
            return io.BytesIO(thumb)
        return None

    def get_meta(self, media_id) -> Union[str, None]:
        meta = media_meta_da.get(media_id)
        if meta:
            return meta.decode()
        return None

    def set_thumb(self, media_id, thumb: io.BytesIO):
        if self.is_readonly:
            raise Exception("Not configured for writing")
        media_thumb_da.set(media_id, thumb.getvalue())

    def set_meta(self, media_id, meta: str):
        if self.is_readonly:
            raise Exception("Not configured for writing")
        media_meta_da.set(media_id, meta)

    def del_thumb(self, media_id):
        if self.is_readonly:
            raise Exception("Not configured for writing")
        raise Exception("Not implemented")

    def del_meta(self, media_id) -> Union[str, None]:
        if self.is_readonly:
            raise Exception("Not configured for writing")
        raise Exception("Not implemented")
