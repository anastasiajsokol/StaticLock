import shutil   # defiles shutil.copyfile
import os       # defines os.path.* and os.curdir

from .response import Response

class Config:
    """Holds all logic for parsing arguments to create command"""

    __slots__ = ["ok", "name", "web", "base", "lisence", "message"]

    def _find(collection: list, item: any):
        """Get the index of item in collection or the value None"""
        # why this does not exist as part of the standard library I may never know
        return collection.index(item) if item in collection else None

    def _suspicious_path(base: str, path: str) -> bool:
        """Check if something strange is going on with the path relative to the base path"""
        base = os.path.abspath(base)
        path = os.path.abspath(path)
        return base != os.path.commonpath([base, path])

    def _complex_path(path: str) -> bool:
        """Check if the provided path has some path interpetation beyond being a directory name"""
        head, tail = os.path.split(path)
        return head != ''
    
    def _read_directory(arguments: list, short_tag: str, full_tag: str, base: str, directory_name: str, base_name: str, default: str) -> tuple:
        """Attempt to read directory specified for web or staticlock base directories"""

        # check if tag even exists
        short_tag_index = Config._find(arguments, short_tag)
        full_tag_index = Config._find(arguments, full_tag)

        if(short_tag_index != None and full_tag_index != None):
            # only one tag or the other is allowed
            return (False, Response("Create", Response.ERROR, f"Either the {short_tag} or {full_tag} can be used, not both"))

        tag = short_tag_index if short_tag_index != None else full_tag_index

        if(tag != None):
            # make sure it is not a trailing tag
            if(tag == len(arguments) - 1):
                # attempted to 
                return (False, Response("Create", Response.ERROR, f"If {directory_name} is manually set, some path must be provided (see README.md for empty path)"))
            
            # read provided path
            directory = arguments[tag + 1]

            # double check that nothing bad is happening... like a backwards path
            if(Config._suspicious_path(base, os.path.abspath(os.path.join(base, directory)))):
                # attempts to do something sneaky with backwards referencing or other iffy constructions, this is not allowed
                return (False, Response("Create", Response.ERROR, f"The {directory_name} must be a subdirectory of the {base_name}"))
            
            # remove arguments
            del arguments[tag + 1]
            del arguments[tag]

            # return overwritten path
            return (True, directory)
        else:
            # simply return default if not overwritten
            return (True, default)
    
    def __init__(self, arguments: list):
        # defaults to being ok
        self.ok = True

        if(len(arguments) == 0):
            # error state
            self.ok = False
            self.message = Response("Create", Response.ERROR, "The create command requires a project name as it's first (and only required) argument")
            return
        
        self.name = arguments[0]

        if(Config._complex_path(self.name)):
            # unable to make a project with a name that can not also be the name of a directory
            self.ok = False
            self.message = Response("Create", Response.ERROR, "The project name must be a valid directory name")
            return

        project_base_path = os.path.join(os.curdir, self.name)  # used later for parsing web base and staticlock base
        
        # prevent the name from later being recognized as anything else
        arguments = arguments[1:]

        # note choice of --liscense
        tag_liscense = Config._find(arguments, "--liscense")
        self.lisence = tag_liscense != None
        if self.lisence:
            # cleanup argument
            del arguments[tag_liscense]
        
        # attempt to parse out -w or --web option
        self.ok, self.web = Config._read_directory(arguments, "-w", "--web", project_base_path, "web base directory", "project base directory", "web")
        if(not self.ok):
            self.message = self.web
            return
        
        # attempt to parse out -b or --base option
        self.ok, self.base = Config._read_directory(arguments, "-b", "--base", os.path.join(project_base_path, self.web), "staticlock base directory", "web base directory", "locked")
        if(not self.ok):
            self.message = self.base
            return

        # at this point - no matter what - arguments should be empty
        if(len(arguments) != 0):
            self.ok = False
            self.message = Response("Create", Response.ERROR, f"Unexpected extra arguments passed to the create command {arguments}")
            return

def run(arguments: list, tool_directory: str) -> Response:
    config = Config(arguments)

    # make sure that parsing the arguments went ok
    if(not config.ok):
        return config.message
    
    project_directory = os.path.join(config.name, "")               # normalize
    web_directory = os.path.join(project_directory, config.web)     # set as subdirectory of project
    staticlock_directory = os.path.join(web_directory, config.base) # set as subdirectory of web

    # create project directory
    try:
        os.mkdir(project_directory)
    except:
        # this means the project directory already exists
        return Response("Create", Response.ERROR, "Unable to create project with same name as an already existing subdirectory")

    # create web base directory
    if web_directory != project_directory:
        os.mkdir(web_directory)

    # create staticlock base directory
    if web_directory != staticlock_directory:
        os.mkdir(staticlock_directory)

    # copy over liscense
    if(config.lisence):
        shutil.copyfile(os.path.join(tool_directory, "LISCENSE"), os.path.join(project_directory, "LISCENSE"))
    
    # create default settings TODO
    
    return Response("Create", Response.OK, f"Created staticlock project {config.name}")
