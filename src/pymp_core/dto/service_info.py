

import json


class ServiceInfo():

    def __init__(self, **kwargs) -> None:
        self.id = kwargs.get("id", "")
        self.roles = kwargs.get("roles", 0)
        self.proto = kwargs.get("proto", "")
        self.host = kwargs.get("host", "")
        self.port = kwargs.get("port", "")

    def to_json(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4)

    @staticmethod
    def from_json(json_string):
        json_dict = json.loads(json_string)
        return ServiceInfo(**json_dict)