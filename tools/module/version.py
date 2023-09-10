from .response import Response

VERSION = "0.1"

def run(arguments: list, _: str) -> Response:
    if(len(arguments) != 0):
        return Response("Version", Response.WARNING, f"StaticLock Toolchain v{VERSION} does not accept arguments to version command")
    return Response("Version", Response.INFO, f"StaticLock Toolchain v{VERSION}")
