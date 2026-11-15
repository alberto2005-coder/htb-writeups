---
machine: Tentacle
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, squid, wpad, opensmtpd, kerberos, keytab]
---

# Tentacle — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Varios proxies Squid y un WPAD revelan redes internas; en una de ellas OpenSMTPD permite ejecución. La autenticación SSH con Kerberos y un keytab dan acceso a más cuentas; un script de backup ejecutado como root cierra la escalada.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,3128,8080 <IP>
curl -x http://<IP>:3128 http://<INTERNAL>/
# WPAD
curl -x http://<IP>:3128 http://wpad/wpad.dat
proxychains curl http://<INTERNAL>:25/
# Kerberos
kinit -kt <FILE>.keytab <USER>
ssh -K <USER>@<HOST>
find / -name "*.sh" -path "*backup*" 2>/dev/null
```

## Enumeración

- Squid en varios puertos y un archivo WPAD.
- OpenSMTPD accesible desde una red interna.
- SSH con Kerberos, keytab y un script de backup.

## Acceso inicial

Se enumeran los proxies y se usa `proxychains` para alcanzar la red interna. WPAD revela el siguiente proxy; OpenSMTPD es vulnerable a ejecución de comandos y da una shell en el host.

## Escalada de privilegios

El keytab permite autenticarse con Kerberos y acceder a otra cuenta por SSH. Un script de backup ejecutado como root es escribible o usa una ruta controlable; se modifica y se obtiene root.

## Evidencia

- WPAD con la cadena de proxies.
- OpenSMTPD ejecutando comandos.
- Keytab, SSH Kerberos y backup modificado.

## Lecciones aprendidas

- Los proxies internos pueden ser la única ruta a una red.
- Kerberos y los keytabs son credenciales de alto valor.
- Un script de backup root escribible es ejecución directa.

## Mitigación y detección

- Restringir Squid y no publicar WPAD.
- Actualizar OpenSMTPD y segmentar la red.
- Proteger keytabs y scripts de backup; ejecutarlos sin privilegios.

## Referencias

- [0xdf — Tentacle](https://0xdf.gitlab.io/2021/06/19/htb-tentacle.html)
- [MIT Kerberos — keytab](https://web.mit.edu/kerberos/krb5-latest/doc/basic/keytab_def.html)
- [Hack The Box — Tentacle](https://app.hackthebox.com/machines/tentacle)
