from ..response import Response, Entry

VERSION = "0.1"

def run(arguments: list, _: str) -> Response:
    res = Response()
    
    if(len(arguments) != 0):
        res.add(Entry("Version", Response.WARNING, f"The version command does not accept any arguments"))
    
    return res.add(Entry("Version", Response.INFO, f"StaticLock Toolchain v{VERSION}"))
