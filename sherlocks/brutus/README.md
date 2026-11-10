---
sherlock: Brutus
domain: SOC
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [dfir, linux, ssh, brute-force, auth-log, log-analysis]
---


# Brutus — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de investigación; sin respuestas literales de la plataforma.

## Escenario

Un servidor Linux expuesto a Internet ha recibido un volumen anómalo de intentos de autenticación. Se entrega una imagen de disco (o un conjunto de logs de sistema) y hay que reconstruir el ataque: desde dónde se originó, qué cuentas se probaron y si alguna vez se consiguió entrar.

## Evidencias

- Imagen de disco o copia de `/var/log`.
- `auth.log` / `secure` del periodo del incidente.
- `wtmp` y el parser `utmp.py` que entrega el reto.
- Listado de usuarios del sistema (`/etc/passwd`).

```bash
sha256sum brutus.zip
ls -la logs/
wc -l logs/auth.log
```

## Investigación

### 1. Delimitar el incidente

En `auth.log`, los fallos de SSH tienen una forma muy estable:

```text
Failed password for invalid user <nombre> from <IP> port <p> ssh2
Failed password for <usuario> from <IP> port <p> ssh2
```

```bash
grep "Failed password" auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn
```

La IP con miles de intentos es el origen; las demás son ruido de Internet. Con eso se acota la ventana temporal primer/último intento.

### 2. Qué cuentas se atacaron

```bash
grep "Failed password" auth.log | grep -oP 'for (invalid user )?\K\S+' | sort | uniq -c | sort -rn
```

Los nombres que no existen en `/etc/passwd` son diccionario genérico (`admin`, `test`, `oracle`…); los que sí existen indican que el atacante tenía una lista de usuarios válidos o los enumeró antes.

### 3. ¿Hubo acceso?

La pregunta clave del reto:

```bash
grep -E "Accepted (password|publickey)" auth.log
grep -c "Failed password" auth.log
```

Aquí sí hay `Accepted password for root from <IP>`: el brute force **tuvo éxito** y la cuenta comprometida es `root`. La primera sesión se abre y cierra en el mismo segundo (el script confirma credenciales); la segunda, minutos después, es la sesión manual. `wtmp` da la hora exacta y `last`/`lastb` la contrastan.

### 4. Contexto del host

```bash
grep -E "new user|useradd|groupadd" auth.log
ls -la /home
```

Sirve para descartar que el atacante creara una cuenta durante el mismo periodo.

## Conclusiones

- Ataque de fuerza bruta/llenado de credenciales contra SSH desde una única IP.
- Acceso conseguido como `root`, creación de un usuario de persistencia y descarga de un script de enumeración.
- Recomendación inmediata: deshabilitar login por contraseña, mover SSH a clave, `fail2ban` y limitar el acceso por red.

## Lecciones

- `auth.log` responde con precisión a «¿entraron?»: una sola línea `Accepted` cambia toda la conclusión.
- Enumerar usuarios válidos antes del ataque es tan importante como el ataque mismo.
- Un reto de brute force se resuelve contando y agrupando, no leyendo línea a línea.
