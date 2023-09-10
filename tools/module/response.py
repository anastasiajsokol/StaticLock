import datetime

class Response:
    OK = 1
    WARNING = 2
    ERROR = 3
    CUSTOM = 4
    INFO = 5

    def __init__(self, sender: str, status: int, message: str = None):
        if message == None:
            if status == Response.OK:
                message = "OK: request completed"
            elif status == Response.WARNING:
                message = "Warning: something may have been wrong with the request"
            elif status == Response.ERROR:
                message = "Error: something was wrong with the request"
            elif status == Response.CUSTOM:
                message = "Custom: ???"
            elif status == Response.INFO:
                message = "Info: ???"
            else:
                message = f"Unknown: status {status}"
        
        self.sender = sender
        self.status = status
        self.message = message

    def log(self) -> str:
        class colors:
            OK = '\033[30m'
            WARNING = '\033[93m'
            ERROR = '\033[91m'
            DEFAULT = ""
            ENDC = '\033[0m'

        if self.status > 0 and self.status <= 5:
            status = ["ok", "warning", "error", "custom", "info"][self.status - 1]
            color = [colors.OK, colors.WARNING, colors.ERROR, colors.DEFAULT, colors.DEFAULT][self.status - 1]
        else:
            status = "unknown"
            color = colors.WARNING
        
        return f"{color}[{datetime.datetime.now().replace(microsecond=0)}] [{status}] {self.message}{colors.ENDC}"

    def __str__(self):
        if self.status != Response.INFO:
            return self.log()
        else:
            return self.message
