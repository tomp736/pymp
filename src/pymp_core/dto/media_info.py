

import json


class MediaInfo():

    def __init__(self, **kwargs) -> None:
        self.media_id = kwargs.get("media_id", "")
        self.server_id = kwargs.get("server_id", "")

    def to_json(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4)

    @staticmethod
    def from_json(json_string):
        json_dict = json.loads(json_string)
        return MediaInfo(**json_dict)
