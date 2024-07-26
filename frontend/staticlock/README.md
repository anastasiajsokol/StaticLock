# StaticLock Frontend Library

## Javascript API

### Global Configuration Semi-Constants



### Compatibility

To test compatibility you can use the `window.StaticLockAPISupported` or `StaticLockAPISupported` constants.

### Logging and Error Reporting

All logging and error reporting is done by three methods.

The first, `window.staticlock_console`, is for general messages and updates. By default, it is `console.log`.

The second, `window.staticlock_error`, is for error messages that may be helpful in debugging but are not necessarily urgent depending on context. By default, it is `console.error`.

The third, `window.staticlock_reporter`, is for error messages which are important for the user to be aware of quickly. By default, it is `alert`.

Note: if `StaticLockAPISupported` is false, as part of the window load event, the `api.js` script will send a message that StaticLock is not supported through `window.staticlock_reporter`.

### StaticLock Object

#### constructor(path = "/staticlock/service.js", scope = "/")

> Creates a StaticLock object. Path should be the path to the StaticLock service worker file, and scope is the scope you want StaticLock to work on.

#### async get_worker()

> Get the current StaticLock service worker.
> Note: May not yet be fully registered.

## Service Worker