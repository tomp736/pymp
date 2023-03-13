

import io
from typing import Union
from pymp_core.abstractions.providers import FfmpegDataProvider
from pymp_core.app.config import ServiceConfig
from pymp_core.decorators import prom


class FfmpegHttpDataProvider(FfmpegDataProvider):
    
    def __init__(self, service_config: ServiceConfig):
        self.service_config = service_config
        
    def __repr__(self) -> str:
        return "FfmpegHttpDataProvider()"

    def is_readonly(self) -> bool:
        return True

    def is_ready(self) -> bool:
        return True

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def get_thumb(self, media_uri) -> Union[io.BytesIO, None]:
        raise Exception("Not Implemented")

    @prom.prom_count_method_call
    @prom.prom_count_method_time
    def get_meta(self, media_uri) -> Union[str, None]:
        raise Exception("Not Implemented")