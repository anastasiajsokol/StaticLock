from .response import Response

def run(arguments: list, _: str) -> Response:
    # information
    version = "v0.1"
    header = f"StaticLock Toolchain {version}\n"
    base_commands = "\tBase Commands\n\t\t-c, --create for creating a project with a given name\n\t\t-l, --lock for setting a directory to be locked\n\t\t-b, --build for building project\n\t\t-s, --settings for setting configuration\n\t\t-v, --version display version information\n\t\t-h, --help display this message\n"
    sub_commands = "\tSub Commands\n"
    
    sub_create = "\t\tcreate\n\t\t\t-w, --web specify web base directory (default: /web)\n\t\t\t-b, --base specify staticlock base directory (default: /$web/lock)\n\t\t\t--liscense create LISCENSE file with the Unliscense as content\n"
    sub_lock = "\t\tlock\n\t\t\t--rename allows output directory to have a different name than input directory\n\t\t\t-f, --force allow input directory which is inside the /$web directory\n"
    sub_build = "\t\tbuild\n\t\t\t--library to place staticlock library files in specific directory (default: /lib in /$web/$lock)\n"
    sub_settings = "\t\tsettings\n\t\t\t-d, --default to output default configuration\n\t\t\tallows all the same subcommands as create\n"
    sub_help = "\t\thelp\n\t\t\tmay be followed by a base command name to only show information about that command\n"

    sub_commands = "\tSub Commands\n" + sub_create + sub_lock + sub_build + sub_settings + sub_help

    # specialization
    message = ""
    status = Response.INFO

    if(len(arguments) == 1):
        # specialized case
        name = arguments[0]
        if name == "create":
            message = f"StaticLock Toolchain {version} Create\n\t\tTags: -c, --create\n\t\tSub Commands\n" + sub_create[2 + len(name) + 1:]
        elif name == "lock":
            message = f"StaticLock Toolchain {version} Lock\n\t\tTags: -l, --lock\n\t\tSub Commands\n" + sub_lock[2 + len(name) + 1:]
        elif name == "build":
            message = f"StaticLock Toolchain {version} Build\n\t\tTags: -b, --build\n\t\tSub Commands\n" + sub_build[2 + len(name) + 1:]
        elif name == "settings":
            message = f"StaticLock Toolchain {version} Settings\n\t\tTags: -s, --settings\n\t\tSub Commands\n" + sub_settings[2 + len(name) + 1:]
        elif name == "version":
            message = f"StaticLock Toolchain {version} Version\n\t\tTags: -v, --version\n"
        elif name == "help":
            message = f"StaticLock Toolchain {version} Help\n\t\tTags: -h, --help\n\t\tSub Commands\n" + sub_help[2 + len(name) + 1:]
        else:
            status = Response.ERROR
            message = f"StaticLock Toolchain {version} does not have a command [{name}] "
    else:
        if(len(arguments) != 0):
            # error case
            status = Response.WARNING
            message = f"StaticLock Toolchain {version} only accepts one optional argument to the help command, not {len(arguments)}\n"
        
        # normal case (possibly composed with error case)
        message += header + base_commands + sub_commands
        
    return Response("Help", status, message + "Please see the README.md file for more information")
