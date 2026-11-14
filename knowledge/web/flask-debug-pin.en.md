---
topic: PIN del depurador de Flask
tags: [web, flask, werkzeug, debug, rce]
---

# PIN del depurador de Flask

[🌐 Español](flask-debug-pin.md) | **English**

## Concept

Werkzeug protects the interactive console with a PIN derived from host data: username, `machine-id`, MAC, module path and process name. If the debugger is exposed, the PIN can be calculated or leaked, turning the console into remote code execution.

## When it applies

- Flask with `debug=True` or `use_debugger=True`.
- The Werkzeug console is reachable from the network.
- `/etc/machine-id`, `/proc/self/cgroup` or the app source can be read.

## Procedure

1. Trigger an exception to open `/console`.
2. Collect `username`, `modname`, `getattr(app, "__name__")`, `getattr(app, "__file__")`, MAC and `machine-id`.
3. Compute the PIN with the `werkzeug.debug` algorithm.
4. Enter the PIN and run commands in the frame.

```python
import hashlib
from itertools import chain

# Fill in the host values
probably_public_bits = [username, modname, app_name, modfile]
private_bits = [str(machine_id), str(mac)]
```

## Variants

- PIN leaked through an LFI or an error that prints the environment.
- Console bound to localhost and reached through an SSH tunnel.
- `debug=True` in a container with a predictable `machine-id`.

## Limitations

- The PIN changes with user, path or MAC.
- The debugger may be disabled or filtered.
- The console does not always run as root.

## Mitigation

- Never enable debug in production.
- Block `/console` at the proxy.
- Run the app as an unprivileged user.

## Detection

- 500 responses with a Werkzeug traceback.
- Requests to `/console` and `__debugger__`.
- Unusual child processes of the web server.

## References

- <https://werkzeug.palletsprojects.com/en/stable/debug/>
- <https://flask.palletsprojects.com/en/stable/debugging/>
- <https://attack.mitre.org/techniques/T1190/>
