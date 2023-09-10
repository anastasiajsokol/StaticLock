from .response import Response

def run(arguments: list, _: str) -> Response:
    return Response("Lock", Response.ERROR, "The lock command is not yet implemented")
