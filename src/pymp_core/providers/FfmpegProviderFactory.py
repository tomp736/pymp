


import logging
from typing import List

from pymp_core.app.config_factory import CONFIG_FACTORY
from pymp_core.app.config import PympServerRoles

from pymp_core.abstractions.providers import FfmpegDataProvider

from pymp_core.providers.FfmpegFileDataProvider import FfmpegFileDataProvider
from pymp_core.providers.FfmpegHttpDataProvider import FfmpegHttpDataProvider


def get_ffmpeg_providers(wants_write_access: bool = False) -> List[FfmpegDataProvider]:
    logging.info("GETTING FFMPEG PROVIDERS")
    ffmpeg_providers = []
    
    # configure self
    server_config = CONFIG_FACTORY.get_server_config()
    if server_config.roles & PympServerRoles.FFMPEG_SVC:
        ffmpeg_provider = FfmpegFileDataProvider()
        if ffmpeg_provider.check_data_provider(wants_write_access):
            ffmpeg_providers.append(ffmpeg_provider)

    # configure hardcoded services
    service_configs = CONFIG_FACTORY.get_service_configs()    
    for service_config in service_configs:
        if service_config.roles & PympServerRoles.FFMPEG_SVC:
            ffmpeg_provider = FfmpegHttpDataProvider(service_config)
            if ffmpeg_provider.check_data_provider(wants_write_access):
                ffmpeg_providers.append(ffmpeg_provider)

    return ffmpeg_providers
