---
machine: Browsed
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, chrome, extension, ssrf, pycache]
---

# Browsed — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Los logs de depuración de Chrome revelan una instancia interna de Gitea y una aplicación Flask en localhost. Una extensión maliciosa ejecuta SSRF contra Flask y una inyección aritmética de Bash da RCE. La escalada envenena el bytecode de `__pycache__` que usa un script con sudo.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,3000,5000 <IP>
ffuf -u http://browsed.htb -H "Host: FUZZ.browsed.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
# Logs de Chrome
curl -s http://browsed.htb/logs/chrome_debug.log | grep -iE "gitea|localhost|token"
# Extensión: host_permissions para http://localhost:*/*
# SSRF y aritmética de Bash
curl -s "http://127.0.0.1:5000/render?expr=$((1+1))"
# Pycache
find / -type d -name __pycache__ -writable 2>/dev/null
python3 -c "import py_compile; py_compile.compile('payload.py', cfile='__pycache__/module.cpython-311.pyc')"
sudo /usr/bin/python3 /opt/app/script.py
```

## Enumeración

- Chrome con `--remote-debugging-port` y logs accesibles.
- Gitea interno y una app Flask solo en `127.0.0.1`.
- Script con sudo que importa módulos desde un directorio escribible.

## Acceso inicial

Se leen los logs de Chrome y se obtiene la URL de Gitea y el puerto de Flask. Se instala una extensión controlada que hace peticiones al localhost de la víctima; el parámetro vulnerable llega a una expresión aritmética de Bash y ejecuta comandos.

## Escalada de privilegios

`sudo -l` muestra un script Python que importa un módulo local. El directorio `__pycache__` es escribible; se compila un `.pyc` malicioso con el mismo nombre y la siguiente ejecución de sudo lo carga, dando root.

## Evidencia

- Log de Chrome con la URL de depuración.
- Petición SSRF al Flask interno y callback de shell.
- `.pyc` malicioso cargado por el script con sudo.

## Lecciones aprendidas

- La depuración remota de Chrome expone historial y cookies.
- Una extensión con permisos de host puede alcanzar loopback.
- Python confía en el bytecode si el `.py` no cambió.

## Mitigación y detección

- No exponer el puerto de depuración y borrar sus logs.
- Revisar extensiones y aislar servicios internos.
- Montar `__pycache__` como solo lectura y usar `PYTHONDONTWRITEBYTECODE`.

## Referencias

- [0xdf — Browsed](https://0xdf.gitlab.io/2026/03/28/htb-browsed.html)
- [Chrome — Extension permissions](https://developer.chrome.com/docs/extensions/develop/concepts/declare-permissions)
- [Hack The Box — Browsed](https://app.hackthebox.com/machines/browsed)
