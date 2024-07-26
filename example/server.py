from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl
import os

def run(directory: str, certfile: str, keyfile: str, port: int = 4444):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)
            
    httpd = HTTPServer(('localhost', port), Handler)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile, keyfile)

    httpd.socket = context.wrap_socket(httpd.socket)

    httpd.serve_forever()

if __name__ == "__main__":
    base = os.path.dirname(os.path.realpath(__file__))

    frontend = os.path.normpath(os.path.join(
        base,
        "../frontend"
    ))

    certfile = os.path.join(base, "localhost.pem")
    keyfile = os.path.join(base, "localhost-key.pem")

    print("Serving StaticLock example at https://localhost:4444")

    run(frontend, certfile, keyfile)
