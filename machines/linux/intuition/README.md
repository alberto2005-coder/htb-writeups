---
machine: Intuition
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, xss, file-read, ftp, suricata, ansible, privesc]
---

# Intuition — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Varios vhosts giran alrededor de un compresor de documentos. Un XSS en el reporte de bugs da acceso como desarrollador y luego como admin; el dashboard exporta PDFs con una lectura de archivos basada en `urllib`, lo que filtra credenciales FTP y una clave SSH de `dev_acc`. Los logs de Suricata exponen la contraseña de `lopez`, que puede ejecutar `runner2` como root; el binario llama a `ansible-galaxy` con un nombre controlado y permite inyección de comandos.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` nginx con `comprezzor.htb`.
- `ffuf` descubre `auth.comprezzor.htb`, `report.comprezzor.htb` y `admin.comprezzor.htb`.
- La web principal comprime documentos y el reporte permite adjuntar capturas.

## Enumeración

- El reporte de bugs refleja HTML y ejecuta XSS cuando lo revisa un desarrollador.
- Se roba la sesión de `dev_acc` y, con ella, se accede a un panel que exporta reportes a PDF.
- La exportación usa `urllib` con una URL controlada; una ruta `file://` permite leer archivos del servidor.

## Foothold

Se leen las credenciales FTP y la clave privada de `dev_acc`. Con la clave se entra por SSH.

```bash
ssh -i dev_acc.key dev_acc@comprezzor.htb
```

## Movimiento lateral

La configuración de Suricata registra tráfico y credenciales en claro. En los logs aparece la contraseña de `lopez`, que funciona por SSH.

```bash
grep -R "password" /var/log/suricata/
ssh lopez@comprezzor.htb
```

## Escalada de privilegios

`lopez` puede ejecutar `/opt/runner2/runner2` como root. El binario lee un JSON y llama a `ansible-galaxy role install` con el nombre del rol; un punto y coma en el nombre inyecta un comando.

```bash
echo '{"role": "x; bash"}' > /tmp/r.json
sudo /opt/runner2/runner2 /tmp/r.json
```

## Evidencia

- XSS en reportes y robo de sesión.
- File read de `urllib` y credenciales FTP.
- Clave SSH de `dev_acc`.
- Logs de Suricata y `lopez`.
- `runner2`, `ansible-galaxy` y root.

## Lecciones aprendidas

- Un XSS en un panel interno puede dar acceso a más vhosts.
- `urllib` con esquemas no validados es lectura de archivos.
- Los logs de IDS pueden contener credenciales en claro.
- Un wrapper que llama a `ansible-galaxy` con entrada controlada es inyección.

## Mitigación y detección

- Escapar reportes y usar CSP.
- Validar esquemas y hosts en exportaciones.
- Redactar credenciales en logs y restringir Suricata.
- Usar listas blancas de roles y `escapeshellarg`.

## Referencias

- [0xdf — Intuition](https://0xdf.gitlab.io/2024/09/14/htb-intuition.html)
- [IppSec — Intuition](https://www.youtube.com/watch?v=uUPj4Qj01-0)
- [Hack The Box — Intuition](https://app.hackthebox.com/machines/intuition)
