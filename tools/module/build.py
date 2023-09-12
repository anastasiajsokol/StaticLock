from .response import Response
from .security.encrypt import encrypt

class Config:
    def __init__(self, arguments: list):


def run(arguments: list, _: str) -> Response:
    return Response("Build", Response.ERROR, "The build command is not yet implemented")
