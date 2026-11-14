---
topic: OWA — password spraying con usuarios enumerados
tags: [windows, owa, exchange, password-spray, initial-access]
---

# OWA — password spraying con usuarios enumerados

[🌐 English](owa-password-spray.en.md) | **Español**

## Concepto

OWA expone un formulario de autenticación de Exchange. Con una lista de usuarios válida y una sola contraseña común se prueban muchas cuentas sin superar el umbral de bloqueo por cuenta. Los nombres se pueden obtener de una red social, del directorio o de firmas de correo.

## Cuándo aplica

- OWA está accesible y no exige MFA para todos los usuarios.
- La política de bloqueo permite pocos intentos por cuenta.
- Se dispone de nombres o direcciones de correo de la organización.

## Procedimiento

1. Recopilar usuarios de la web, LinkedIn o del listado de la aplicación.
2. Elegir una contraseña estacional o débil y probar una vez por cuenta.
3. Verificar las credenciales válidas en OWA y en WinRM o SMB.
4. Usar la cuenta para phishing interno o para buscar más recursos.

## Comandos

```bash
# Lista de usuarios obtenida de la web o del directorio
python3 sprayingtoolkit.py -t https://<HOST>/owa/ -U users.txt -p '<PASSWORD>'
# Verificar acceso
curl -k -I https://<HOST>/owa/
```

## Variantes

- Probar la contraseña contra VPN, RDP o WinRM además de OWA.
- Usar el nombre de la empresa y el año para construir variantes.
- Esperar entre rondas para evitar bloqueos y detección.

## Limitaciones

- MFA o Conditional Access bloquean el acceso aunque la contraseña sea válida.
- La política de bloqueo puede dispararse con pocos intentos.
- Las cuentas pueden requerir cambio de contraseña en el primer inicio.

## Mitigación

- Exigir MFA y políticas de bloqueo inteligente.
- Bloquear contraseñas comunes y revisar intentos distribuidos.
- Limitar la exposición de nombres y correos en la web.

## Detección

- Muchos intentos fallidos distribuidos entre cuentas.
- Autenticaciones correctas desde una IP nueva después de fallos.
- Accesos a OWA desde user agents o países inusuales.

## Referencias

- [0xdf — Reel2](https://0xdf.gitlab.io/2021/03/13/htb-reel2.html)
- [Microsoft — Outlook on the web](https://learn.microsoft.com/en-us/exchange/outlook-on-the-web/outlook-web-app)
- [MITRE T1110.003 — Password Spraying](https://attack.mitre.org/techniques/T1110/003/)
