from ..response import Response
from .security import encrypt

class Config:
    def __init__(self, arguments: list):
        pass

def run(arguments: list, _: str) -> Response:
    return Response("Build", Response.ERROR, "The build command is not yet implemented")
