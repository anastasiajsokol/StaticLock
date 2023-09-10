# Static Lock Toolchain

A system for adding password-locked content to static websites.

## Development Tools

The development command line tool is named `staticlock` and serves to make it easy for you to secure directories before deploying your static site.

    WARNING: unlocked raw directories should not be uploaded to the site if they should be 'locked', make sure that you only upload the corresponding locked directory

#### Command Line Interface

There are a number of base commands, it is required at least on of these is used. Each may be followed by sub commands to customize execution.

    -c, --create must be followed by a name for the project, setups project in a subdirectory of the current directory with the provided name

        this command can be used with -w or --web to specify the web base directory (highly recommended not an empty path) defaults to 'web'
            note: to set web base directory to project directory you must understand enough to enter an empty path
        this command can be used with -b or --base to specify the lock base directory relative to the web base directory (recommended not to be an empty path) defaults to 'locked'
        this command can be used with --liscense to also provide a copy of The Unliscense (you will have to setup other liscense systems yourself)
    
    -l, --lock followed by the raw directory to lock, when page is built will output to a directory of the same name in the lock base directory

        this command can be used with -f or --file to specify the configuration file to use, defaults to staticlock.json in project directory
        this command can be used with --rename followed by a new name to place directory in a lock base subdirectory with the new name instead of same name
        this command can be used with -f or --force to prevent the default error if the raw directory is also in the web base
            warning: if this is the case it is likely that an unlocked version of your directory will also be hosted, only use -f if you have a good reason
    
    -b, --build builds the current project using the configuration file

        this command can be used with -f or --file to specify the configuration file to use, defaults to staticlock.json (see docs/staticlock/configuration.md for format)
        this command can be used with --library followed by an output directory to specify a path relative to the web directory to place the static lock library files
    
    -v, --version print a short message with the version information of the staticlock command, note that the command tool and library should be the same

    -h, --help prints out a help page similar to this section

        this command may be followed by a base command name, doing so will limit the output to just explain that tag

## Library

The Static Lock library should be hosted on your site. This consists of a javascript module which will need to be used on any page that manages permissions and a service worker which will be setup by the module when its use becomes necessary for your application. You will also need to upload a json map of your encrypted directories into the base directory, this is auto generated by the `staticlock` tool and will be used by both the library and the service worker to verify passwords and know where to look for encrypted files. Note that this json map will leak the names of your encrypted directories (ie if you setup an encrypted directory /movies then a user could use the json map to know that there is a directory named /movies, depending on what information your server gives it may also be possible to know how many files are in a given directory and get a general idea of how big each file is, however the raw names of these files will not be made public - unless if you leak it yourself in an unencrypted directory).

## Installation 

Installation instructions are only supported for modern versions of Ubuntu with python installed, however overall the installation process is not difficult to adapt. 

First download the files into whatever directory you use to store tools (if you do not have one yet, I recommend `~/Tools`, `~/Downloads/tools`, or `~/Code/tools`) using `git clone https://github.com/anastasiajsokol/StaticLock.git`. Then enter the downloaded repository using `cd StaticLock`.

There are a couple ways to properly alias the `staticlock` command. The first thing is you will need to know the absolute path of the file `tools/staticlock.py`. If you have the command `realpath` installed you can get this by running `realpath tools/staticlock.py` from the repository root directory, otherwise you will have to get it some other way (whatever the tools directory you choose, plus `/StaticLock/tools/staticlock.py`).

Then there are two options. If you have python installed to `/usr/bin/python` (check by running `/usr/bin/python --version`) then you can use `alias staticlock=PATH` replacing `PATH` with whatever the absolute directory you used is. Otherwise, use `alias staticlock="python3 PATH"` - possibly switching out the python command for whatever command it is setup as on your system and again switching out `PATH` for the absolute path you found.

To make the alias persistant across terminal sessions add the alias command to your `~/.bashrc` or equivalent file.