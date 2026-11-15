---
machine: Calamity
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, php, stego, suid, buffer-overflow]
---

# Calamity — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una página que ejecuta PHP arbitrario da el foothold web. El esteganografiado de un audio revela la contraseña de un usuario para SSH. La escalada explota un binario SUID con desbordamientos de buffer por etapas hasta controlar el flujo y ejecutar como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
gobuster dir -u http://calamity.htb -w /usr/share/wordlists/dirb/common.txt
curl -s "http://calamity.htb/admin.php?cmd=id"
# Esteganografía
steghide extract -sf audio.wav
audacity audio.wav
# SUID
find / -perm -4000 -type f 2>/dev/null
checksec --file=/usr/local/bin/<BIN>
gdb -q /usr/local/bin/<BIN>
python3 exploit.py
```

## Enumeración

- Aplicación PHP con un editor o ejecutor de código accesible.
- Archivo de audio con datos ocultos y un usuario SSH.
- Binario SUID no estándar con entrada controlable.

## Acceso inicial

Se descubre una página que evalúa PHP y se usa para ejecutar comandos. En el sistema se localiza un audio; `steghide` o Audacity extraen una cadena que resulta ser la contraseña de SSH de un usuario.

## Escalada de privilegios

`find / -perm -4000` muestra un binario propio. `checksec` confirma NX y canary, pero el programa encadena lecturas y desbordamientos por etapas que permiten filtrar direcciones y sobrescribir el retorno. Se construye el exploit con pwntools y se lanza para obtener root.

## Evidencia

- Ejecución PHP y shell inicial.
- Audio con la contraseña extraída.
- Fuga de direcciones, offset de retorno y shell de root.

## Lecciones aprendidas

- La esteganografía sigue siendo un canal de secretos.
- Un SUID con entrada de usuario exige auditoría de memoria.
- Las fugas por etapas convierten un canary en un obstáculo superable.

## Mitigación y detección

- No permitir ejecución de PHP desde la web.
- Retirar binarios SUID innecesarios y compilar con mitigaciones completas.
- No ocultar credenciales en archivos públicos.

## Referencias

- [0xdf — Calamity](https://0xdf.gitlab.io/2020/08/27/htb-calamity.html)
- [GDB — Debugging](https://sourceware.org/gdb/documentation/)
- [Hack The Box — Calamity](https://app.hackthebox.com/machines/calamity)
