---
machine: Principal
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, spring-boot, pac4j, jwt, cve-2026-29000, password-spray, ssh-ca, privesc]
---

# Principal — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Aplicación Spring Boot con pac4j para autenticación JWT. La CVE-2026-29000 permite forjar JWT cifrados usando solo la clave pública RSA del servidor (JWKS), saltándose la verificación de firma y entrando al dashboard. En los ajustes aparece una `encryptionKey` que se prueba como contraseña contra SSH; un password spray con Hydra encuentra que es válida para `svc-deploy`. Para root se abusa de la clave privada de la CA SSH en `/opt/principal/ssh`, propiedad del grupo `deployers`: se firma un certificado para el principal `root` y se entra por SSH.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,8080 <IP>
```

- `22`: OpenSSH 9.6p1 Ubuntu.
- `8080`: Jetty, aplicación Spring Boot.

```bash
echo '<IP> principal.htb' | sudo tee -a /etc/hosts
feroxbuster -u http://principal.htb:8080 -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeración

La aplicación tiene un login y un dashboard. El endpoint de configuración pública expone el JWKS con la clave RSA. La versión de pac4j es 6.0.3, anterior a las versiones corregidas de la CVE-2026-29000.

La documentación y el código indican que los JWT se cifran además de firmarse, y que la verificación de firma puede omitirse si el token está cifrado con la clave pública.

## Foothold

La CVE-2026-29000 permite construir un JWT cifrado con la clave pública del servidor y un `sub` arbitrario. El servidor lo descifra, no valida la firma y acepta la identidad. Con el token se entra al dashboard como un usuario con privilegios.

Dentro del dashboard, la configuración muestra una `encryptionKey` usada para proteger datos internos. Se guarda la lista de usuarios y se lanza un password spray contra SSH:

```bash
hydra -L users.txt -p '<ENCRYPTION_KEY>' ssh://<IP>
```

La clave funciona para `svc-deploy`.

## Movimiento lateral

No hay otro host. `svc-deploy` pertenece al grupo `deployers`. `/opt/principal/ssh` es propiedad de `root:deployers` y contiene la clave privada de la CA SSH y su configuración.

## Escalada de privilegios

Con la clave de la CA se firma un certificado para el principal `root`. El servidor confía en los certificados de esa CA, así que el certificado permite autenticarse como root sin conocer su contraseña.

```bash
cd /opt/principal/ssh
ssh-keygen -t ed25519 -f /tmp/root
ssh-keygen -s ca -I root -n root /tmp/root.pub
ssh -i /tmp/root root@127.0.0.1
```

## Evidencia

- JWKS público y versión de pac4j 6.0.3.
- JWT cifrado forjado y acceso al dashboard.
- `encryptionKey` leída de los ajustes.
- Password spray con Hydra y login SSH como `svc-deploy`.
- Grupo `deployers` y acceso a `/opt/principal/ssh`.
- Certificado firmado para `root` y `id` con UID 0.

## Lecciones aprendidas

- Un JWT cifrado no sustituye la verificación de firma; hay que validar ambas.
- La clave pública no es un secreto, pero no debe permitir forjar identidades.
- Reutilizar una clave de cifrado como contraseña de SSH es un fallo grave.
- Una CA SSH mal protegida permite emitir certificados para cualquier principal.
- Los grupos de despliegue deben tener acceso mínimo y auditoría.

## Mitigaciones y detección

- Actualizar pac4j a una versión corregida y validar siempre la firma.
- No aceptar JWT cifrados de emisores no confiables sin comprobar `iss`, `aud` y algoritmo.
- Separar claves de cifrado, firmas y contraseñas; no reutilizarlas.
- Proteger la clave privada de la CA SSH con permisos 600 y fuera de grupos amplios.
- Auditar la emisión de certificados y los principals solicitados.
- Alertar de JWKS consultados desde IPs externas, sprays SSH y certificados para `root`.

## Referencias

- [0xdf — Principal](https://0xdf.gitlab.io/2026/03/30/htb-principal.html)
- [IppSec — Principal](https://www.youtube.com/watch?v=w0h0gkvOn0c)
- [Hack The Box — Principal](https://app.hackthebox.com/machines/principal)
- [NVD — CVE-2026-29000](https://nvd.nist.gov/vuln/detail/CVE-2026-29000)
- [Knowledge — Bypass de autenticación en pac4j-jwt](../../../knowledge/web/pac4j-jwt-auth-bypass.md)
