---
machine: Compiled
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, web, git, gitea, hashcat, privesc]
---

# Compiled — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una web que compila repositorios Git usa una versión vulnerable de Git; un repositorio con submódulos maliciosos ejecuta código en el servidor. La base SQLite de Gitea local filtra hashes de usuarios, uno de ellos reutilizado por SSH. La escalada abusa de una versión vulnerable de Visual Studio para llegar a SYSTEM.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,3000,5985 <IP>
```

- Puertos: `22/tcp` SSH, `80/tcp` HTTP, `3000/tcp` Gitea y `5985/tcp` WinRM.
- Servicios: Portal de compilación, Gitea local y OpenSSH para Windows.
- Tecnologías: Git, Gitea, SQLite, PBKDF2-SHA256, Visual Studio.

## Enumeración

- `compiled.htb` permite registrar una cuenta y enviar una URL de repositorio.
- Gitea escucha en `127.0.0.1:3000`.
- Base `gitea.db` con usuarios y hashes.
- OpenSSH expuesto para usuarios del sistema.

## Foothold

Se crea un repositorio con un submódulo y un hook que aprovecha CVE-2024-32002. Al solicitar la compilación, Git clona el submódulo y ejecuta el hook como el usuario del servicio.

```bash
# Repositorio local con submódulo y hook malicioso
python3 create_cve_2024_32002_repo.py
# Enviar la URL del repositorio a la web de compilación
curl -s -b cookies.txt -F "repo=http://<IP>/repo.git" http://compiled.htb/compile
```

## Movimiento lateral

La shell permite leer la base de Gitea y extraer los hashes. Se reformatea el hash PBKDF2 y se crackea; la contraseña se reutiliza para SSH.

## Escalada de privilegios

La enumeración muestra una instalación vulnerable de Visual Studio. Se aprovecha su componente de actualización/instalador para ejecutar código con privilegios de SYSTEM.

```bash
whoami /priv
wmic product get name,version
# Localizar el instalador y lanzar el exploit correspondiente a la versión
C:\\Program Files (x86)\\Microsoft Visual Studio\\Installer\\vs_installer.exe
```

## Evidencia

- Repositorio aceptado y callback del hook.
- Tabla de usuarios de Gitea y hash crackeado.
- Acceso SSH y shell como SYSTEM.

## Lecciones aprendidas

- Un servicio que clona repositorios es una frontera de confianza crítica.
- Las bases SQLite de herramientas internas suelen contener hashes reutilizados.
- El software de desarrollo instalado amplía la superficie de escalada.

## Mitigación y detección

- Actualizar Git y deshabilitar hooks/submódulos en clones no confiables.
- Aislar Gitea y usar hashes lentos con sal única.
- Actualizar Visual Studio y ejecutar servicios con cuentas de bajo privilegio.

## Referencias

- [0xdf — Compiled](https://0xdf.gitlab.io/2024/12/14/htb-compiled.html)
- [IppSec — Compiled](https://www.youtube.com/watch?v=aG_N2ZiCfxk)
- [Hack The Box — Compiled](https://app.hackthebox.com/machines/compiled)
