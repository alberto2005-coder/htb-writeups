---
machine: Socket
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, flask, websocket, sqlite, pyinstaller, sudo]
---

# Socket — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El sitio de QReader ofrece un cliente de escritorio empaquetado con PyInstaller. Al desempaquetarlo y decompilarlo se descubre un endpoint WebSocket que habla con SQLite sin parametrizar. Una inyección UNION filtra el hash de `admin`, que se crackea y permite SSH como `tkeller`. El usuario puede ejecutar un script de build que llama a PyInstaller como root; un `.spec` malicioso ejecuta código y entrega root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80,5789 <IP>
```

- SSH, Flask/Werkzeug y un servicio WebSocket en 5789.
- `qreader.htb` y `ws.qreader.htb`.
- El sitio permite descargar `QReader_lin_v0.0.2.zip` y la versión Windows.

## Enumeración

- El binario Linux es un bundle PyInstaller.
- `pyinstxtractor` recupera los `.pyc` y `pycdc` reconstruye el código.
- El cliente envía la versión a `ws://ws.qreader.htb:5789/version`.
- La consulta SQLite concatena el valor recibido.

## Foothold

Se replica el mensaje WebSocket y se inyecta una consulta UNION de cuatro columnas. La tabla de usuarios devuelve `admin` y un hash MD5; se crackea, se prueba reutilización y se accede por SSH como `tkeller`.

```bash
python3 -c 'import websocket; ...'
hashcat -m 0 <HASH> rockyou.txt
```

## Escalada de privilegios

`sudo -l` muestra un script `build-installer.sh` que root ejecuta. El script acepta un `.spec` y llama a PyInstaller; se controla el contenido del spec y se ejecuta código durante el build como root. También se puede usar para copiar un archivo privilegiado.

```bash
sudo /usr/local/sbin/build-installer.sh build <FILE>.spec
```

## Evidencia

- Desempaquetado del bundle y código del cliente.
- Petición WebSocket con la inyección y filas devueltas.
- Sesión SSH como `tkeller`.
- `sudo -l` y build de PyInstaller ejecutado como root.

## Lecciones aprendidas

- Los binarios empaquetados con PyInstaller no ocultan el código.
- Un WebSocket puede ser una API SQL completa.
- Ejecutar builds como root convierte un archivo de configuración en ejecución de código.

## Mitigaciones y detección

- Parametrizar las consultas SQLite y validar el tipo de los mensajes.
- No confiar en un cliente por estar compilado.
- Ejecutar builds en un contenedor sin privilegios y revisar los `.spec`.
- Alertar de procesos `pyinstaller` como root y de escrituras en el directorio de build.
- Referencias: HTB Socket, 0xdf, CWE-89.

## Referencias

- <https://www.hackthebox.com/machines/Socket>
- <https://0xdf.gitlab.io/2023/07/15/htb-socket.html>
- <https://cwe.mitre.org/data/definitions/89.html>
- <https://attack.mitre.org/techniques/T1059/>
