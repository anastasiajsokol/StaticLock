import os   # defines os.path.*

from .response import Response

class Config:
    __slots__ = ["ok", "message", "file", "input", "output"]

    def _find(collection: list, item: any) -> any:
        """Get the index of item in collection or the value None"""
        # why this does not exist as part of the standard library I may never know
        return collection.index(item) if item in collection else None

    def _is_subdirectory(base: str, path: str) -> bool:
        base = os.path.abspath(base)
        path = os.path.abspath(path)
        return base != path and base == os.path.commonpath([base, path])

    def __init__(self, arguments: list):
        self.ok = True

        if(len(arguments) == 0):
            # must have at least an input directory
            self.ok = False
            self.message = Response("Lock", Response.ERROR, "The lock command requires a path to the directory to be locked")
            return
        
        # remove the input directory from arguments
        self.input = arguments[0]
        arguments = arguments[1:]

        # check force arguments first (since it is used later)
        short_force = Config._find(arguments, "-f")
        long_force = Config._find(arguments, "--force")

        force = short_force if short_force != None else long_force  # defining both is not great, but not worth throwing an error over, at least not yet

        if(force != None):
            # in this case do not check input and output directories for sanity, remove from arguments
            del arguments[force]
        
        force = force != None   # convert to a boolean just for easier use later

        # TODO finish

def run(arguments: list, _: str) -> Response:
    return Response("Lock", Response.ERROR, "The lock command is not yet implemented")
