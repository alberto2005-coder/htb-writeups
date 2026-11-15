---
machine: Faculty
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, sqli, mpdf, meta-git, gdb, ptrace]
---

# Faculty — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una SQLi en el login de la aplicación escolar permite entrar como administrador. Una función de mPDF lee archivos y expone la contraseña de la base, reutilizada por un usuario local. `meta-git` ofrece inyección de comandos y el GDB de ese usuario tiene `CAP_SYS_PTRACE`, suficiente para inyectar en un proceso de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
# SQLi de login
sqlmap --url "http://faculty.htb/login.php" --data="username=admin&password=x" --batch
# mPDF file read
curl -s "http://faculty.htb/pdf.php?template=../../../../etc/passwd"
# meta-git
meta-git clone 'git@github.com:x/y.git; id'
# GDB con capacidad
getcap $(which gdb)
gdb -p <ROOT_PID> -ex "call system(\"id\")" -ex quit
```

## Enumeración

- Aplicación escolar con login y generación de PDF.
- mPDF accesible desde un parámetro de plantilla o archivo.
- Usuario con `meta-git` y GDB con capacidad `cap_sys_ptrace`.

## Acceso inicial

Se bypassa el login con una SQLi y se accede al panel. La funcionalidad de PDF acepta una ruta y mPDF la resuelve, lo que permite leer archivos; la configuración de la base contiene una contraseña reutilizada por SSH.

## Escalada de privilegios

Con la cuenta local se ejecuta `meta-git`, que pasa argumentos a Git sin sanear; se inyecta un comando para pivotar a otro usuario. Ese usuario puede usar GDB con `cap_sys_ptrace`; se adjunta a un proceso de root y ejecuta `call system`.

## Evidencia

- Login bypass con SQLi.
- Archivo leído mediante mPDF y contraseña de SSH.
- Inyección en meta-git y `call system` desde GDB.

## Lecciones aprendidas

- Las librerías de PDF pueden leer archivos si aceptan rutas.
- Las credenciales de base reutilizadas amplían el acceso.
- Una capacidad de ptrace equivale a ejecución en otros procesos.

## Mitigación y detección

- Parametrizar consultas y restringir plantillas PDF.
- No reutilizar contraseñas entre servicios.
- Eliminar `cap_sys_ptrace` de GDB y limitar `meta-git`.

## Referencias

- [0xdf — Faculty](https://0xdf.gitlab.io/2022/10/22/htb-faculty.html)
- [mPDF — Documentation](https://mpdf.github.io/)
- [Hack The Box — Faculty](https://app.hackthebox.com/machines/faculty)
