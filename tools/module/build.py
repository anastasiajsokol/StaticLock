from .response import Response

def run(arguments: list, _: str) -> Response:
    return Response("Build", Response.ERROR, "The build command is not yet implemented")
