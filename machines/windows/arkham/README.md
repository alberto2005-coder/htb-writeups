---
machine: Arkham
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, smb, luks, jsf, deserialization, winrm]
---

# Arkham — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un share SMB contiene un ZIP con una imagen LUKS y una nota. La imagen se descifra y revela la configuración de Tomcat/JSF, incluida la clave de ViewState. La deserialización de Java en `userSubscribe.faces` da shell como `alfred`. Un OST de Outlook guarda credenciales de `batman`, y WinRM más un bypass de UAC llevan a Administrator.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
80/tcp    http    Microsoft IIS 10.0
135/tcp   msrpc
139/tcp   netbios-ssn
445/tcp   smb
8080/tcp  http    Apache Tomcat / JSF
49666/tcp msrpc
49667/tcp msrpc
```

## Enumeración

- El share `batshare` es accesible sin credenciales y contiene `appserver.zip`.
- El ZIP incluye `IMPORTANT.txt` y `backup.img`, una imagen LUKS.
- El sitio de 8080 usa JSF con `*.faces` y estado en servidor.
- La enumeración de SMB y del host sugiere un entorno Windows con Tomcat.

## Foothold

La contraseña de la imagen LUKS se obtiene con una wordlist y `bruteforce-luks`. Al montarla aparecen los ficheros de Tomcat y `web.xml.bak`, que expone `org.apache.myfaces.SECRET` y el algoritmo MAC.

Con esa clave se construye un ViewState malicioso: se serializa un payload de `ysoserial` con `CommonsCollections5`, se cifra en DES-ECB, se firma con HMAC-SHA1 y se envía en el campo oculto de `userSubscribe.faces`.

```bash
bruteforce-luks -f wordlist.txt backup.img
mount /dev/mapper/<MAPPER> /mnt
python3 jsf_payload.py '<COMMAND>'
```

## Movimiento lateral

La shell inicial es `alfred`. En su escritorio hay un `backup.zip` con un OST de Outlook. Se extraen los mensajes y se recuperan credenciales de `arkham\batman`.

Con `New-PSSession` o WinRM se abre una sesión como `batman`, que pertenece a un grupo administrativo.

```powershell
New-PSSession -ComputerName . -Credential $cred
Enter-PSSession -Session $s
```

## Escalada de privilegios

La sesión de `batman` permite ejecutar comandos con privilegios elevados, pero el proceso sigue con un token filtrado. Se usa un bypass de UAC basado en un binario auto-elevado para lanzar una shell con el token completo de Administrator.

```powershell
whoami /groups
# elegir un bypass UAC compatible con la versión de Windows
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales, si existen, viven en `private/` y no se publican.

## Lecciones aprendidas

- Un backup de disco puede contener secretos de aplicación en texto claro.
- La clave de ViewState convierte JSF en una superficie de deserialización.
- Los OST de Outlook son una fuente habitual de credenciales.
- Pertenecer a Administrators no elimina el filtrado de UAC.

## Mitigaciones y detección

- Cifrar backups y restringir el acceso a shares sensibles.
- Rotar claves de JSF y no guardar configuración en backups accesibles.
- Deshabilitar el acceso anónimo a SMB y auditar shares.
- Aplicar UAC en modo máximo y revisar binarios auto-elevados.

## Referencias

- [0xdf — Arkham](https://0xdf.gitlab.io/2019/08/10/htb-arkham.html)
- [Búsqueda de vídeos (CSV)](https://www.youtube.com/results?search_query=ippsec+arkham)
- [Búsqueda de writeups (CSV)](https://medium.com/search?q=hackthebox+arkham+writeup)
