"""
    Testing Server
        replace with static server in development!
        note that to use web crypto api and service workers either localhost or https is needed
    
    self-signed ssl option
        openssl req  -nodes -new -x509  -keyout cert/key.pem -out cert/cert.pem
    
    while this is generally ok for local testing, DO NOT use it for anything else
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl
import os

HTTPS = False

web_directory = os.path.join(os.path.dirname(__file__), "src")

os.chdir(web_directory)

httpd = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)

if HTTPS:
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
else:
    print("Serving at http://localhost:8000")

httpd.serve_forever()
