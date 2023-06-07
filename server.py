"""
    Server - must support https
        (replace with static server in development)
    
    self-signed ssl for access to web crypto
        openssl req  -nodes -new -x509  -keyout cert/key.pem -out cert/cert.pem
    
    note that while this is generally ok for local testing, DO NOT use it for anything else
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl
import os

certificate_directory = os.path.join(os.path.dirname(__file__), "cert")
web_directory = os.path.join(os.path.dirname(__file__), "src")

os.chdir(web_directory)

httpd = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)

certificate_directory = os.path.join(os.path.dirname(__file__), "cert")
keyfile = os.path.join(certificate_directory, "key.pem")
certfile = os.path.join(certificate_directory, "cert.pem")

httpd.socket = ssl.wrap_socket (
            httpd.socket, 
            keyfile = keyfile, 
            certfile = certfile,
            server_side = True
        )

print("Serving at https://0.0.0.0:8000")

httpd.serve_forever()
