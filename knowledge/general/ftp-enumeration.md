---
topic: FTP enumeration
tags: [general, ftp, enumeration, anonymous, upload, vsftpd]
---

# FTP enumeration

[🌐 English](ftp-enumeration.en.md) | **Español**

## Concepto

FTP expone archivos y, a menudo, permite escritura anónima o credenciales débiles. La enumeración busca versiones vulnerables, directorios accesibles, archivos de configuración y la posibilidad de subir un webshell o un script.

## Cuándo aplica

- Puerto 21 abierto.
- Banner `vsftpd`, `ProFTPD` o `FileZilla Server`.
- Acceso anónimo o invitado.
- Directorio de subidas dentro de un webroot.

## Procedimiento

1. Identificar el servicio y la versión.
2. Probar acceso anónimo.
3. Listar directorios y descargar archivos relevantes.
4. Buscar credenciales, backups y claves.
5. Probar escritura y ejecución desde el webroot.

```bash
ftp <HOST>
# usuario: anonymous, contraseña vacía
wget -m --no-passive ftp://anonymous:anonymous@<HOST>/
curl -s ftp://anonymous:anonymous@<HOST>/ --list-only
```

## Variantes

- `vsftpd 2.3.4` con backdoor conocido.
- FTP con TLS y certificado débil.
- Subida de `.php`, `.aspx` o `.war`.
- Montaje NFS o SMB del mismo directorio.

## Limitaciones

- El acceso anónimo puede estar deshabilitado.
- El firewall puede permitir control pero no datos pasivos.
- El webroot puede no ser el directorio FTP.
- La subida puede requerir permisos especiales.

## Mitigación y detección

- Deshabilitar FTP anónimo y usar SFTP.
- Restringir escritura y separar el webroot.
- Actualizar el servidor y limitar la exposición.
- Alertar de logins anónimos, transferencias masivas y subidas ejecutables.

## Referencias

- <https://www.rfc-editor.org/rfc/rfc959>
- <https://attack.mitre.org/techniques/T1021/002/>
- <https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-ftp/index.html>
