---
topic: Timeroasting — cuentas de equipo por SNTP
tags: [windows, active-directory, timeroasting, ntp, kerberos]
---

# Timeroasting — cuentas de equipo por SNTP

[🌐 English](timeroasting.en.md) | **Español**

## Concepto

Timeroasting solicita respuestas SNTP para cuentas de equipo y obtiene material derivado de su contraseña. El hash resultante se crackea fuera de línea y puede dar acceso como la cuenta máquina, que a menudo tiene privilegios sobre el dominio.

## Cuándo aplica

- El DC responde a SNTP y permite consultas para cuentas de equipo.
- Se conoce el nombre o SID de equipos del dominio.
- Las contraseñas de equipo son débiles o antiguas.

## Procedimiento

1. Enumerar cuentas de equipo y sus SID.
2. Solicitar respuestas SNTP con `timeroast.py`.
3. Crackear los hashes con Hashcat o John.
4. Usar la cuenta máquina para enumerar y escalar.

## Comandos

```bash
timeroast.py -d <DOMAIN> -u <USER> -p "<PASS>"
hashcat -m 31300 hashes.txt /usr/share/wordlists/rockyou.txt
# Alternativa
john --format=timeroast hashes.txt
nxc smb <DC> -u '<MACHINE>$' -p "<PASS>"
```

## Variantes

- Combinar con un usuario de dominio para enumerar SID.
- Usar la cuenta máquina para RBCD o lectura de recursos.
- Probar el hash contra otros equipos.

## Limitaciones

- Microsoft puede requerir autenticación para SNTP.
- Las contraseñas de equipo rotan y pueden ser fuertes.
- El crackeo depende de la entropía y del diccionario.

## Mitigación

- Restringir SNTP y exigir autenticación.
- Rotar contraseñas de equipo y usar cuentas gestionadas.
- Monitorizar consultas SNTP anómalas.

## Detección

- Muchas solicitudes SNTP para cuentas de equipo.
- Autenticaciones con cuentas máquina desde hosts no habituales.
- Uso de Hashcat contra hashes de equipo.

## Referencias

- [Secura — Timeroasting](https://www.secura.com/blog/timeroasting)
- [0xdf — RustyKey](https://0xdf.gitlab.io/2025/11/08/htb-rustykey.html)
- [MITRE — T1557](https://attack.mitre.org/techniques/T1557/)
