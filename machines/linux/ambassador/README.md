---
machine: Ambassador
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, grafana, cve-2021-43798, directory-traversal, consul, credentials]
---

# Ambassador — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Grafana 8.2.0 es vulnerable a CVE-2021-43798 y permite leer archivos arbitrarios. Con `grafana.db` se obtienen usuarios y hashes; las credenciales permiten acceder a Consul y escalar por un servicio mal configurado.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p22,80,3000,8500 <IP>
```

Se añade `ambassador.htb` al hosts. Grafana corre en el puerto 3000 y Consul en 8500.

## Acceso inicial

Se confirma Grafana 8.2.0 y se explota el directory traversal de plugins:

```bash
curl --path-as-is 'http://<IP>:3000/public/plugins/alertlist/../../../../../../etc/passwd'
```

Se descarga `grafana.db`:

```bash
curl --path-as-is 'http://<IP>:3000/public/plugins/alertlist/../../../../../../var/lib/grafana/grafana.db' -o grafana.db
```

Se extraen usuarios y hashes con `sqlite3`. El hash se crackea o se reutiliza una contraseña.

## Movimiento lateral

Con las credenciales se accede a Consul. Se enumeran servicios, nodos y claves KV; puede haber tokens o scripts con credenciales de SSH.

## Escalada a root

Se identifica un servicio o tarea de Consul que se ejecuta como root y acepta configuración del usuario. Se registra un servicio malicioso o se modifica un script para obtener una shell root.

## Evidencia

- Versión de Grafana y respuesta del traversal.
- `grafana.db` y hash redactado.
- Acceso a Consul.
- Servicio modificado y shell root.

## Lecciones aprendidas

- Grafana antiguo filtra archivos fuera del webroot.
- `grafana.db` contiene usuarios y secretos.
- Consul sin ACLs expone topología y configuración.
- Los servicios de orquestación pueden ejecutar como root.

## Mitigación y detección

- Actualizar Grafana a una versión corregida.
- Restringir el puerto 3000 y aplicar autenticación.
- Proteger `grafana.db` y rotar credenciales.
- Configurar ACLs en Consul y revisar servicios.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2021-43798>
- <https://www.hackthebox.com/machines/ambassador>
- <https://developer.hashicorp.com/consul/docs/security/acl>
