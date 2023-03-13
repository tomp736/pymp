
from flask import Flask
from prometheus_client import start_http_server
import logging

from pymp_core.app.config import PympServerRoles
from pymp_core.app.config_factory import CONFIG_FACTORY
from pymp_core.app.services import MEDIA_REGISTRY_SERVICE, MEDIA_SERVICE, FFMPEG_SERVICE

from pymp_server.routes.mediaregistry import app_mediaregistry
from pymp_server.routes.media import app_media
from pymp_server.routes.ffmpeg import app_ffmpeg_meta
from pymp_server.routes.ffmpeg import app_ffmpeg_thumb
from pymp_server.routes.frontend import app_frontend_media
from pymp_server.routes.frontend import app_frontend_thumb
from pymp_server.routes.frontend import app_frontend_meta

app = Flask(__name__)


def main():
    logging.getLogger().setLevel(logging.INFO)
    start_http_server(8000)
    
    server_config = CONFIG_FACTORY.get_server_config()
    flask_config = CONFIG_FACTORY.get_flask_config()
    
    logging.info(server_config.__dict__)

    # HOW TO DO SWITCH STATEMENT
    if server_config.roles & PympServerRoles.MEDIA_API:
        app.register_blueprint(app_frontend_media)

    if server_config.roles & PympServerRoles.THUMB_API:
        app.register_blueprint(app_frontend_thumb)

    if server_config.roles & PympServerRoles.META_API:
        app.register_blueprint(app_frontend_meta)

    if server_config.roles & PympServerRoles.MEDIAREGISTRY_SVC:
        MEDIA_REGISTRY_SERVICE.watch_services()
        app.register_blueprint(app_mediaregistry)

    if server_config.roles & PympServerRoles.FFMPEG_SVC:
        FFMPEG_SERVICE.watch_media()
        app.register_blueprint(app_ffmpeg_meta)
        app.register_blueprint(app_ffmpeg_thumb)

    if server_config.roles & PympServerRoles.MEDIA_SVC:
        MEDIA_SERVICE.watch_media()
        app.register_blueprint(app_media)

    app.run(
        host=flask_config.host,
        port=flask_config.port,
        debug=False
    )


if __name__ == '__main__':
    main()
