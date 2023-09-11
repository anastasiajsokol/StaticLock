import os   # defines os.path.*

from .response import Response

class Config:
    """Parse input arguments into safe fields"""
    __slots__ = ["ok", "message", "file", "input", "output", "force"]

    def _find(collection: list, item: any) -> any:
        """Get the index of item in collection or the value None"""
        # why this does not exist as part of the standard library I may never know
        return collection.index(item) if item in collection else None

    def _is_subdirectory(base: str, path: str) -> bool:
        """Check if path is subdirectory of base"""
        base = os.path.abspath(base)
        path = os.path.abspath(path)
        return base != path and base == os.path.commonpath([base, path])
    
    def _read_argument(arguments: list, tag: str, default: str) -> tuple:
        """Attempt to read tag"""
        index = Config._find(arguments, tag)

        if(index == None):
            return (True, default)

        if(index == len(arguments) - 1):
            return (False, Response("Lock", Response.ERROR, f"Expected a path following the {tag} tag"))
        
        path = arguments[index + 1]

        del arguments[index + 1]
        del arguments[index]

        return (True, path)

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
        force = Config._find(arguments, "--force")
        
        if(force != None):
            # in this case do not check input and output directories for sanity, remove from arguments
            del arguments[force]
        
        self.force = force != None

        # get output directory
        self.ok, self.output = Config._read_argument(arguments, "--rename", self.input)

        if(not self.ok):
           self.message = self.input
           return 
        
        # get configuration file
        self.ok, self.file = Config._read_argument(arguments, "--file", "staticlock.json")

        if(not self.ok):
            self.message = self.file
            return

def run(arguments: list, _: str) -> Response:
    config = Config(arguments)
    
    if(not config.ok):
        return config.message

    return Response("Lock", Response.ERROR, "The lock command is not yet implemented")
