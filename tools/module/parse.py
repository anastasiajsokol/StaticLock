from .response import Response, Entry

class Parser:
    def __init__(self, arguments: list):
        # store different kinds of arguments
        self._flags = set()
        self._mapped = {}
        self._positions = []

        # for providing feedback
        self.response = Response()

        # allow for finer control over indexing
        index = 0
        while index < len(arguments):
            argument = arguments[index]

            if(argument[0] == '-'):
                if(len(argument) == 1 or (argument[1] == '-' and len(argument) == 2)):
                    self.response.add(Entry("Parser", Response.WARNING, "Bad argument, nameless marker"))
                
                if(argument[1] == '-'):
                    # tagged parameter
                    if(index == len(arguments) - 1):
                        self.response.add(Entry("Parser", Response.ERROR, f"Tagged argument [{argument}] must be followed by a value"))
                        return
                    value = arguments[index + 1]
                    index += 1 # skip over value
                    if(value[0] == '-'):
                        self.response.add(Entry("Parser", Response.WARNING, "Tagged argument has a value which is also a tag"))
                else:
                    # tagged flag
                    self._flags.add(argument[1:])
            else:
                # positional
                self._positions.append(argument)

            index += 1
    
    def tagged(self, name: str, default: any) -> any:
        """get tagged argument, or default if not provided"""
        return self._mapped.get(name, default)
    
    def flag(self, name: str) -> bool:
        """check for flag"""
        return name in self._flags

    def position(self, index: int, default: any) -> any:
        """attempt to read value at position"""
        return self._positions[index] if index < len(self._positions) else default
    
    def length(self) -> int:
        """get number of positional arguments"""
        return len(self._positions)

    def __contains__(self, name: str) -> bool:
        """check if name is a tagged argument"""
        return name in self._mapped

    def __bool__(self):
        """check if the object is valid (aka no errors)"""
        return self.response.status < Response.ERROR
