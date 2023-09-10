#!/usr/bin/python

"""
    staticlock build tool version 0.1
        repository  https://github.com/anastasiajsokol/StaticLock
        author      Anastasia Sokol
        lisense     The Unliscense (see repository for more information)
"""

# command state response interface
from module.response import Response

# base command modules
import module.create as create
import module.lock as lock
import module.build as build
import module.version as version
import module.help as help

# dispatch to base command module
def commandinterface(command: str, subcommands: list, tool_directory: str) -> Response:
    # map commands onto corresponding modules
    module_map = {
        '-c': create,
        '--create': create,
        '-l': lock,
        '--lock': lock,
        '-b': build,
        '--build': build,
        '-v': version,
        '--version': version,
        '-h': help,
        '--help': help
    }

    # run module (if it exists)
    if command in module_map:
        return module_map[command].run(subcommands, tool_directory)
    else:
        return Response("Command Interface", Response.ERROR, f"No staticlock base command corresponds to tag '{command}', use -h or --help for more information")

if __name__ == "__main__":
    from sys import argv, exit
    from os import path

    if len(argv) == 1:
        # without a base command staticlock can not do anything
        print(Response("Command Parser", Response.ERROR, "the staticlock build tool requires at least a base command, use the command -h or --help for more information"))
        exit(1)
    
    tool, command, *arguments = argv

    # first get realpath of staticlock.py script, then get the only the directory name, then reference directory below, and finally use abspath to apply '..'
    tool_directory = path.abspath(path.join(path.dirname(path.realpath(tool)), '..'))

    # commandinterface will return a Response object, which if called directly should be printed to standard output
    print(commandinterface(command, arguments, tool_directory))
