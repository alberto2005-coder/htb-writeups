---
machine: University
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, ad, reportlab, wpad, rbcd, delegation, gmsa]
---

# University — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El generador de PDF usa ReportLab y es vulnerable a CVE-2023-33733, lo que da una shell como `WAO`. Un script de PowerShell filtra credenciales reutilizadas en el host y en dos contenedores. Un archivo URL malicioso ejecuta código como revisor, se envenena WPAD para relayar NTLM y se crea un equipo con RBCD. El contenedor tiene delegación sin restricciones; sus tickets llevan a una GMSA que puede actuar ante el DC.

## Reconocimiento

```bash
nmap -Pn -sCV -p53,80,88,135,139,389,445,464,636,3268,3269,5985,9389 <IP>
```

- `53/88/389/445/636` confirman un DC de `university.htb`.
- `80/tcp` nginx redirige a la web; `5985/tcp` WinRM está abierto.
- El sitio permite registrar profesores y exportar el perfil a PDF.

## Enumeración

- La exportación usa ReportLab y procesa HTML; CVE-2023-33733 permite ejecutar código al generar el PDF.
- Un script de PowerShell en el host contiene credenciales de `WAO` que también funcionan en los contenedores.
- `bloodhound` revela la delegación sin restricciones y la GMSA del servicio.

## Foothold

Se envía un payload de CVE-2023-33733 en el campo del perfil y se obtiene una reverse shell como `WAO` al exportar el PDF.

```bash
# registrar profesor y poner el payload en el campo vulnerable
# exportar el perfil a PDF y recibir la shell
nc -lnvp 443
```

## Movimiento lateral

Con `WAO` se enumeran SMB y los contenedores. Se genera un paquete de clase con un archivo `.url` malicioso que ejecuta código como revisor. Desde esa sesión se fuerza la búsqueda WPAD y se envenena la respuesta desde el contenedor Linux, lo que permite relayar NTLM y crear un equipo con RBCD.

## Escalada de privilegios

El contenedor Windows tiene delegación sin restricciones. Se extraen los tickets Kerberos de memoria, se identifica una cuenta que puede leer la GMSA y se usa `getST.py`/RBCD para actuar como administrator en el DC.

```bash
Rubeus.exe monitor /interval:5 /nowrap
Rubeus.exe ptt /ticket:<BASE64>
certipy-ad account read -u <USER> -p '<PASSWORD>' -dc-ip <IP> -target dc.university.htb
getST.py -spn cifs/dc.university.htb -impersonate administrator university.htb/<GMSA>$
```

## Evidencia

- PDF con CVE-2023-33733 y shell como `WAO`.
- Credenciales reutilizadas y ejecución como revisor.
- WPAD relay, RBCD, tickets de delegación y GMSA.

## Lecciones aprendidas

- La generación de PDF con HTML puede ejecutar código.
- Las credenciales de scripts y backups suelen reutilizarse entre hosts.
- WPAD y la delegación sin restricciones permiten movimientos laterales profundos.

## Mitigación y detección

- Actualizar ReportLab y aislar la generación de PDF.
- Rotar credenciales y no reutilizarlas entre contenedores.
- Deshabilitar WPAD, limitar la delegación y proteger las GMSA.

## Referencias

- [0xdf — University](https://0xdf.gitlab.io/2025/08/09/htb-university.html)
- [IppSec — University](https://www.youtube.com/watch?v=q9ms9k02fUM)
- [Hack The Box — University](https://app.hackthebox.com/machines/university)
