---
sherlock: Telly
category: SOC
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [soc, pcap, telnet, cve-2026-24061, exfiltration]
---

# Telly — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Un MSSP analiza el tráfico de un servidor de backups poco usado. Una solución DLP marca una posible exfiltración. Se entrega un PCAP de una hora y se pide reconstruir el acceso y la salida de datos.

## Evidencias

- `monitoringservice_export_202610AM-11AM.pcapng` (unos 23.000 paquetes).
- Tráfico Telnet, HTTP y conexiones externas.
- No se entrega disco ni memoria.

```bash
capinfos monitoringservice_export_202610AM-11AM.pcapng
tshark -r capture.pcapng -q -z io,phs
```

## Investigación

### 1. Inventario y triaje

Se revisan protocolos y conversaciones. Telnet en claro permite leer credenciales y comandos; una sesión desde una IP externa es el primer indicador.

```bash
tshark -r capture.pcapng -Y 'telnet' -T fields -e ip.src -e ip.dst -e telnet.data
```

### 2. Línea temporal

Se sigue el stream TCP principal:
- Conexión al servicio Telnet.
- Comandos de enumeración.
- Creación de una cuenta de servicio.
- Descarga de un script de persistencia.
- Lectura y compresión de una base de datos.

La vulnerabilidad asociada es CVE-2026-24061 en `telnetd` (GNU InetUtils), que permite autenticación como root.

### 3. Artefacto clave

El stream contiene la creación de la cuenta y la descarga de `linper.sh`. Después se observa la exfiltración de un archivo de base de datos de tarjetas; el atacante lo borra al final.

## Conclusiones

- El acceso inicial fue Telnet exploitable, no fuerza bruta.
- El atacante creó persistencia y exfiltró datos de clientes.
- El tráfico en claro permitió reconstruir toda la cadena.
- Hay que rotar credenciales y revisar el servidor.

## Lecciones

- Telnet no debe estar expuesto.
- El tráfico de gestión sin cifrar facilita el DFIR y el ataque.
- La exfiltración puede ocurrir en pocos minutos.

## Referencias

- <https://www.hackthebox.com/sherlocks/Telly>
- <https://nvd.nist.gov/vuln/detail/CVE-2026-24061>
- <https://attack.mitre.org/techniques/T1048/>
