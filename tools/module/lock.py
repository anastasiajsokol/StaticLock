import os   # defines os.path.*
import json # defines json.load

from .response import Response, Entry
from .version import VERSION

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
            return (False, Response().add(Entry("Lock", Response.ERROR, f"Expected a path following the {tag} tag")))
        
        path = arguments[index + 1]

        del arguments[index + 1]
        del arguments[index]

        return (True, path)

    def __init__(self, arguments: list):
        self.ok = True

        if(len(arguments) == 0):
            # must have at least an input directory
            self.ok = False
            self.message = Response().add(Entry("Lock", Response.ERROR, "The lock command requires a path to the directory to be locked"))
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
           self.message = self.output
           return 
        
        # get configuration file
        self.ok, self.file = Config._read_argument(arguments, "--file", "staticlock.json")

        if(not self.ok):
            self.message = self.file
            return
        
        if(len(arguments) != 0):
            self.ok = False
            self.message = Response().add(Entry("Lock", Response.ERROR, f"Unexpected extra arguments passed to the lock command {arguments}"))
            return

def run(arguments: list, _: str) -> Response:
    config = Config(arguments)
    
    if(not config.ok):
        return config.message
    
    # attempt to read configuration file
    data = {}

    try:
        with open(config.file, "r") as configuration:
            data = json.load(configuration)
    except:
        return Response().add(Entry("Lock", Response.ERROR, f"Unable to open configuration file {config.file} for reading"))

    # make sure versions match
    if(data.get("version", None) == None):
        return Response().add(Entry("Lock", Response.ERROR, f"Provided configuration [{config.file}] does not have a version field"))
    elif(data["version"] != VERSION):
        return Response().add(Entry("Lock", Response.ERROR, f"Version of configuration file does not match the version of this tool [{data['version']} is not {VERSION}] look into updating the tool or migrating your project"))

    # map out structure
    project_base = os.path.abspath(os.curdir)
    web_base = None
    staticlock_base = None

    try:
        web_base = os.path.join(project_base, data["web"])
        staticlock_base = os.path.join(web_base, data["base"])
    except:
        return Response().add(Entry("Lock", Response.ERROR, f"Unable to read information about project directory structure from provided configuration [{config.file}]"))
    
    # get directories entry
    directories = data.get("directories")

    if(directories == None):
        return Response().add(Entry("Lock", Response.ERROR, f"Unable to read current directory information from [{config.file}]"))

    if(not config.force):
        # make sure that this entry will not be messing with another entry
        for directory in directories:
            if(directory.get("input") == config.input):
                return Response().add(Entry("Lock", Response.ERROR, f"There is already a lock entry for input {config.input}"))
            if(directory.get("output") == config.output):
                return Response().add(Entry("Lock", Response.ERROR, f"There is already a lock entry outputing to {config.output}"))

        # check that input and output directories are "safe" (where they should be)
        if(Config._is_subdirectory(web_base, os.path.join(project_base, config.input))):
            return Response().add(Entry("Lock", Response.ERROR, "Unable to lock a directory located in web base directory - see README.md for more information, warnings, and workarounds"))
        if(not Config._is_subdirectory(staticlock_base, os.path.join(staticlock_base, config.output))):
            return Response().add(Entry("Lock", Response.ERROR, "The output directory should be a subdirectory of the staticlock base - see README.md for more information, warnings, and workarounds"))

    directories.append({
        "input": config.input,
        "output": config.output
    })

    # attempt to write data back to configuration
    data["directories"] = directories

    try:
        with open(config.file, "w") as configuration:
            json.dump(data, configuration)
    except:
        return Response().add(Entry("Lock", Response.ERROR, f"Unable to write new configuration back to file {config.file}"))

    return Response().add(Entry("Lock", Response.OK, f"Locked {config.input} to {config.output}"))
