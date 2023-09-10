from .response import Response

def run(arguments: list, _: str) -> Response:
    return Response("Settings", Response.ERROR, "The settings command is not yet implemented")
