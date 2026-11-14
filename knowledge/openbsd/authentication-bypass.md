---
topic: OpenBSD — bypass de autenticación y S/Key
tags: [openbsd, authentication, bypass, xlock, skey]
---

# OpenBSD — bypass de autenticación y S/Key

[🌐 English](authentication-bypass.en.md) | **Español**

## Concepto

Un fallo en `auth_userokay()` puede hacer que servicios basados en BSD auth acepten una autenticación sin una contraseña válida. En OpenKeyS se combina con `xlock` y S/Key para pasar de usuario a root.

## Cuándo aplica

- OpenBSD sin los parches de 2019.
- Servicios que usan BSD auth, como `su`, `doas` o `xlock`.
- S/Key habilitado para una cuenta.

## Procedimiento

1. Identificar la versión de OpenBSD.
2. Probar la autenticación en servicios BSD auth.
3. Comprobar `xlock` y la configuración de S/Key.
4. Obtener una sesión y revisar privilegios.
5. Escalar con el fallo local correspondiente.

## Comandos

```bash
uname -a
cat /etc/skey/skeys 2>/dev/null
xlock -help
```

## Variantes

- Bypass remoto en SSH o `su`.
- Escalada local con `xlock`.
- Abuso de S/Key para persistencia.

## Limitaciones

- Requiere una versión vulnerable.
- El servicio debe usar auth_userokay.
- Los parches de 2019 lo mitigan.

## Mitigación

- Actualizar OpenBSD y aplicar los parches de 2019.
- Revisar la configuración de S/Key y `xlock`.
- Limitar servicios expuestos.

## Detección

- Autenticaciones exitosas sin contraseña válida.
- Uso anómalo de `xlock` y S/Key.

## Referencias

- <https://www.openbsd.org/errata.html>
- <https://nvd.nist.gov/vuln/detail/CVE-2019-19521>
