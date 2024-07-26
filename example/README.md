# Example Server

## Rationale

It is not possible (on most platforms) to access the Web Crypto API without a secure connection, so in order to test StaticLock locally it is necessary to provide a secure connection to localhost. The example server serves the example frontend. Note that the `frontend/staticlock` directory contains the actual frontend library (though you are free to implement your own of course) but may be moved or renamed if more convenient, however the `staticlock.js` file must be located in the root directory of your application.

## Instructions

It is recommended to use `mkcert` on Linux. After installing for your specific platform (for example, `sudo apt install mkcert`) run `mkcert localhost` in the example directory, then `mkcert -install`. The tool will likely ask for root privileges and possibly other tools (such as `libnss3-tools`) to complete the installation.

Afterwards you should have `localhost-key.pem` and `localhost.pem` files in the example directory, and you are good to go by simply running the `server.py` script.