---
sherlock: Psittaciformes
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, linux, bash-history, git, log-analysis, web]
---

# Psittaciformes — Hack The Box (Sherlock)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Un servidor Linux presenta actividad sospechosa y un repositorio Git con cambios no explicados. Se pide reconstruir el acceso, los comandos ejecutados y el código introducido por el atacante.

## Evidencias

- `auth.log`, `syslog` y logs del servicio web.
- `.bash_history` de las cuentas relevantes.
- Repositorio Git con historial y ramas.
- Archivos de configuración y tareas cron.

```bash
sha256sum <EVIDENCE>.zip
7z l <EVIDENCE>.zip
```

## Investigación

### 1. Acceso y sesión

Se buscan inicios de sesión aceptados, fallos repetidos y creación de usuarios. La IP de origen se cruza con los logs de SSH y con el primer comando registrado en el historial.

```bash
grep -Ei 'accepted|failed|new user|sudo' auth.log
```

### 2. Historial de comandos

`.bash_history` no tiene marcas de tiempo por defecto; se ordena con los eventos de autenticación y con los `atime`/`mtime` de los archivos tocados. Se identifican descargas, cambios de permisos y ejecución de scripts.

- Comandos de reconocimiento.
- Transferencia de herramientas.
- Edición de código o configuración.
- Persistencia mediante cron o servicio.

### 3. Repositorio Git

Se revisan `git log`, `git diff` y los objetos sueltos. Los commits del atacante pueden estar ocultos en ramas, reflog o blobs sin referencia.

```bash
git log --all --oneline --decorate
git reflog
git fsck --lost-found
```

El código modificado se compara con la versión desplegada para determinar si el cambio llegó a producción.

## Conclusiones

- Cuenta e IP de acceso.
- Comandos y archivos modificados.
- Commit o blob con el cambio malicioso.
- IOCs: rutas, nombres y hashes, redactados.

## Lecciones

- El historial de shell sin timestamps necesita correlación externa.
- Git conserva objetos aunque el commit ya no esté en una rama.
- Un cambio en el repositorio no implica que se haya desplegado.

## Referencias

- <https://www.hackthebox.com/sherlocks/Psittaciformes>
- <https://attack.mitre.org/techniques/T1070/003/>
- <https://git-scm.com/docs/git-fsck>
- <https://www.git-scm.com/book/en/v2/Git-Internals-Git-Objects>
