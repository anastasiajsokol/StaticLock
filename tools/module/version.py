from .response import Response

def run(arguments: list) -> Response:
    if(len(arguments) != 0):
        return Response("Version", Response.WARNING, "StaticLock Toolchain v0.1 does not accept arguments to version command")
    return Response("Version", Response.INFO, "StaticLock Toolchain v0.1")
