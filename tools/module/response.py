import datetime

class Response:
    INFO = 0
    OK = 1
    WARNING = 2
    ERROR = 3

    def __init__(self, status = 1):
        self.status = status
        self.entries = []
    
    def add(self, entry: any):
        if(entry.status > self.status):
            self.status = entry.status
        self.entries.append(entry)
        return self
    
    def addall(self, entries: list):
        def joined(first: any, rest: iter) -> iter:
            yield first
            for item in rest:
                yield item
        
        self.status = max(joined(self.status, entries), key = lambda entry : entry.status)
        self.entries.append(*entries)
        return self
    
    def __iter__(self) -> iter:
        for entry in self.entries:
            yield entry

    def __str__(self) -> str:
        return '\n'.join((str(entry) for entry in self))

class Entry:
    def __init__(self, sender: str, status: int, message: str = None):
        if message == None:
            if status == Response.INFO:
                message = "Info: ???"
            elif status == Response.OK:
                message = "OK: request completed"
            elif status == Response.WARNING:
                message = "Warning: something may have been wrong with the request"
            elif status == Response.ERROR:
                message = "Error: something was wrong with the request"
            else:
                message = f"Unknown: status {status}"
        
        self.sender = sender
        self.status = status
        self.message = message
        self.time = datetime.datetime.now()

    def log(self) -> str:
        class colors:
            OK = '\033[30m'
            WARNING = '\033[93m'
            ERROR = '\033[91m'
            DEFAULT = ""
            ENDC = '\033[0m'

        if self.status > 0 and self.status <= 5:
            status = ["info", "ok", "warning", "error"][self.status]
            color = [colors.DEFAULT, colors.OK, colors.WARNING, colors.ERROR][self.status]
        else:
            status = "unknown"
            color = colors.WARNING
        
        return f"{color}[{self.time.replace(microsecond=0)}] [{status}] {self.message}{colors.ENDC}"

    def __str__(self) -> str:
        if self.status != Response.INFO:
            return self.log()
        else:
            return self.message
