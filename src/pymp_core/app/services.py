
from pymp_core.app.config_factory import CONFIG_FACTORY
from pymp_core.services.FfmpegService import FfmpegService
from pymp_core.services.MediaRegistryService import MediaRegistryService
from pymp_core.services.MediaService import MediaService


server_config = CONFIG_FACTORY.get_server_config()
MEDIA_SERVICE = MediaService(server_config)
MEDIA_REGISTRY_SERVICE = MediaRegistryService(server_config)
FFMPEG_SERVICE = FfmpegService(server_config)
