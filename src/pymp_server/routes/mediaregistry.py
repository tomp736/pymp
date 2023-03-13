import json
import logging
import uuid
from flask import Response
from flask import request
from flask import Blueprint

from pymp_core.app.services import MEDIA_REGISTRY_SERVICE
from pymp_core.dto.media_info import MediaInfo
from pymp_core.dto.service_info import ServiceInfo

app_mediaregistry = Blueprint('app_mediaregistry', __name__)


@app_mediaregistry.route('/registry/service')
def get_registry_service_list():
    service_infos = MEDIA_REGISTRY_SERVICE.get_media_registry_provider().get_all_service_info()
    json_response = json.dumps(service_infos, default=lambda o: o.__dict__,  sort_keys=True, indent=4)
    return Response(json_response, status=200, content_type="application/json")


@app_mediaregistry.route('/registry/service/<string:server_id>')
def get_registry_service(server_id):
    service_infos = MEDIA_REGISTRY_SERVICE.get_media_registry_provider().get_all_service_info()
    service_info = service_infos[server_id]
    json_response = json.dumps(service_info, default=lambda o: o.__dict__,  sort_keys=True, indent=4)
    return Response(json_response, status=200, content_type="application/json")


@app_mediaregistry.route('/registry/service', methods=['POST'])
def post_registry_service():
    if request.json:
        service_info = ServiceInfo.from_json(request.json)

        if service_info.id == "":
            service_info.id = str(uuid.uuid4())

        if not service_info is None:
            MEDIA_REGISTRY_SERVICE.register_service(service_info)
            return Response(service_info.to_json(), content_type="application/json")

    return Response({
        "success": False
    }, content_type="application/json", status=400)


@app_mediaregistry.route('/registry/media')
def get_registry_media_list():
    media_infos = MEDIA_REGISTRY_SERVICE.get_media_registry_provider().get_all_media_info()
    json_response = json.dumps(media_infos, default=lambda o: o.__dict__,  sort_keys=True, indent=4)
    return Response(json_response, status=200, content_type="application/json")


@app_mediaregistry.route('/registry/media/<string:media_id>')
def get_registry_media(media_id):
    media_info = MEDIA_REGISTRY_SERVICE.get_media_info(media_id)
    json_response = json.dumps(media_info, default=lambda o: o.__dict__,  sort_keys=True, indent=4)
    return Response(json_response, status=200, content_type="application/json")


@app_mediaregistry.route('/registry/media')
def post_registry_media():
    if request.json:
        media_info = MediaInfo.from_json(request.json)
        MEDIA_REGISTRY_SERVICE.register_media(media_info)
        return Response({
            "success": True
        })

    return Response({
        "success": False
    }, status=400)


@app_mediaregistry.route('/registry/media/index')
def get_registry_media_index():
    media_infos = MEDIA_REGISTRY_SERVICE.get_media_registry_provider().get_all_media_info()
    if not media_infos is None:
        json_response = json.dumps(media_infos, default=lambda o: o.__dict__,  sort_keys=True, indent=4)
        return Response(json_response, status=200, content_type="application/json")

    return Response(status=503)


@app_mediaregistry.after_request
def after_request(response):
    return response
