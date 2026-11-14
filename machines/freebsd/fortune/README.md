---
machine: Fortune
os: FreeBSD
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [freebsd, command-injection, certificates, authpf, nfs]
---

# Fortune — Hack The Box (FreeBSD)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El selector de `fortune` en 80 es vulnerable a inyección de comandos. Con eso se leen la clave y el certificado de la CA intermedia, se genera un certificado de cliente y se accede al HTTPS de 443, que explica `authpf`. `authpf` abre NFS sobre `/home`; con UID spoofing se añade una clave SSH y se entra como `bob` o `charlie`. Las credenciales de pgAdmin dan root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
22/tcp   ssh
80/tcp   http
443/tcp  https   client certificate required
2049/tcp nfs     after authpf
```

## Enumeración

- El formulario de 80 envía `db=<selección>` a `/select`.
- El parámetro se concatena en una llamada a `fortune`; `;id` confirma ejecución.
- El HTTPS de 443 pide certificado de cliente y revela una CA intermedia.
- La inyección permite leer `/home/bob/ca` y la clave privada de la CA.

## Foothold

Se confirma la inyección y se enumeran archivos con el usuario `_fortune`. La CA intermedia permite firmar un certificado de cliente; se importa en el navegador o se usa con `curl`.

```bash
curl -s -X POST http://<IP>/select -d 'db=;id'
openssl req -new -key client.key -out client.csr
openssl x509 -req -in client.csr -CA intermediate.cert.pem   -CAkey intermediate.key.pem -CAcreateserial -out client.pem -days 1
curl -k --cert client.pem --key client.key https://<IP>/
```

## Movimiento lateral

El sitio de 443 indica que se use `authpf`. Se conecta por SSH con la clave proporcionada y se activa el anchor de `pf`, que abre NFS y otros puertos internos.

Con NFS sobre `/home` y `no_all_squash`, se crea un directorio `.ssh` y un `authorized_keys` con la clave del atacante, suplantando el UID de `bob` o `charlie`.

```bash
ssh -i authpf.key authpf@<IP>
showmount -e <IP>
sudo mount -t nfs <IP>:/home /mnt/home
```

## Escalada de privilegios

La base de datos de pgAdmin contiene credenciales de un usuario con privilegios. Se reutilizan para cambiar a root o para conectarse al servicio administrativo.

```bash
sqlite3 /var/lib/pgadmin/pgadmin4.db 'select * from server;'
su -
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales, si existen, viven en `private/` y no se publican.

## Lecciones aprendidas

- Concatenar entrada en una línea de comandos es RCE directo.
- Una CA de cliente accesible desde la aplicación anula la autenticación mutua.
- `authpf` solo protege si el usuario no puede modificarse a sí mismo.
- NFS con `no_all_squash` permite escribir como otros UIDs.
- Las bases de datos de herramientas administrativas guardan secretos.

## Mitigaciones y detección

- Usar listas permitidas y `execve` sin shell para `fortune`.
- Guardar la clave de la CA fuera del servidor web y rotarla.
- Exportar `/home` con `all_squash` y solo a hosts concretos.
- Cifrar credenciales de pgAdmin y restringir su base de datos.

## Referencias

- [0xdf — Fortune](https://0xdf.gitlab.io/2019/08/03/htb-fortune.html)
- [Búsqueda de vídeos (CSV)](https://www.youtube.com/results?search_query=ippsec+fortune)
- [Búsqueda de writeups (CSV)](https://medium.com/search?q=hackthebox+fortune+writeup)
