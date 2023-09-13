# StaticLock Toolchain

Tool for smoothly adding password protected content without a trusted oracle.

The newist version is still in active development and some features may not be functional at a given point in time, check out the stable directory for a fully working version!

## Development Tool

The development command line tool is named `staticlock` and serves to make it easy for you to secure directories before deploying your static site.

    WARNING: unlocked raw directories should not be uploaded to the site if they should be 'locked', make sure that you only upload the corresponding locked directory

#### Command Line Interface

    create
        description: create a new project as a subdirectory of the current directory
        positional:
            name of project, must be a 'simple' path
        tags:
            --web can be used to specify the project web directory, defaults to 'web'
                WARNING: must not be an empty path and may not be a backreference
            --locked can be used to specify where to place locked content, defaults to 'locked'
            --library specify web subpath to place the library files
        flags:
            -liscense provides a copy of The Unliscense for the newly created project
    
    lock
        description: setup a lock entry in the configuration file
        position:
            raw directory to lock
        tags:
            --file specify a configuration file to use, defaults to 'staticlock.json'
            --rename specify a different name for the output file than the input
        flags:
            -force do not validate paths
                warning: this can result in unsecure configurations

    build
        description: build a specific configuration
        position:
            none
        tags:
            --file specify the configuration file to read, defaults to 'staticlock.json'
        flags:
            none
    
    version
        description: print out the current version
        position:
            none
        tags:
            none
        flags:
            none
    
    help
        description: print out usage information for the tool
        position
            optional command name, if used only shows related information
        tags:
            none
        flags:
            none

## Library

The Static Lock library should be hosted on your site. This consists of a javascript module which will need to be used on any page that manages permissions and a service worker which will be setup by the module when its use becomes necessary for your application. You will also need to upload a json map of your encrypted directories into the base directory, this is auto generated by the `staticlock` tool and will be used by both the library and the service worker to verify passwords and know where to look for encrypted files. Note that this json map will leak the names of your encrypted directories (ie if you setup an encrypted directory /movies then a user could use the json map to know that there is a directory named /movies, depending on what information your server gives it may also be possible to know how many files are in a given directory and get a general idea of how big each file is, however the raw names of these files will not be made public - unless if you leak it yourself in an unencrypted directory).

## Installation 

Installation instructions are only supported for modern versions of Ubuntu with python installed, however overall the installation process is not difficult to adapt. 

First download the files into whatever directory you use to store tools (if you do not have one yet, I recommend `~/Tools`, `~/Downloads/tools`, or `~/Code/tools`) using `git clone https://github.com/anastasiajsokol/StaticLock.git`. Then enter the downloaded repository using `cd StaticLock`.

There are a couple ways to properly alias the `staticlock` command. The first thing is you will need to know the absolute path of the file `tools/staticlock.py`. If you have the command `realpath` installed you can get this by running `realpath tools/staticlock.py` from the repository root directory, otherwise you will have to get it some other way (whatever the tools directory you choose, joined with `StaticLock/tools/staticlock.py`).

Then there are two options. If you have python installed to `/usr/bin/python3` (check by running `/usr/bin/python3 --version`) then you can use `alias staticlock=PATH` replacing `PATH` with whatever the absolute path you found was. Otherwise, use `alias staticlock="python3 PATH"` - possibly switching out the python command for whatever command it is setup as on your system and again switching out `PATH` for the absolute path you found.

To make the alias persistant across terminal sessions add the alias command to your `~/.bashrc` or equivalent file.
