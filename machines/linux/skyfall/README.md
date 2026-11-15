---
machine: Skyfall
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, web, minio, vault, fuse, ssh-otp, privesc]
---

# Skyfall — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

MinIO 2023 es vulnerable a CVE-2023-28432 y filtra las credenciales de root. Con ellas se lee un backup que contiene un token de Vault y su política permite generar credenciales SSH OTP para `askyy`. `vault-unseal` se ejecuta con sudo y escribe un `debug.log` de root; con FUSE se captura ese log, se obtiene el token maestro y se accede al rol SSH de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH en Ubuntu 22.04 y `80/tcp` nginx con `skyfall.htb`.
- El vhost `demo.skyfall.htb` aloja una aplicación con login.
- `feroxbuster` descubre `/metrics` y una ruta bloqueada que apunta a MinIO.

## Enumeración

- Una inconsistencia de parsing permite alcanzar MinIO a través de nginx.
- MinIO es vulnerable a CVE-2023-28432, que filtra `MINIO_ROOT_USER` y `MINIO_ROOT_PASSWORD`.
- Con esas credenciales se listan buckets y se descarga un backup de `home_backup`.

## Foothold

En el backup aparece un `VAULT_TOKEN` en `.bashrc`. El token puede listar `ssh/*` y crear credenciales en `ssh/creds/dev_otp_key_role`; se usa `vault ssh` para entrar como `askyy`.

```bash
curl -s http://demo.skyfall.htb/.../minio/bootstrap/v1/verify
export VAULT_ADDR=http://prd23-vault-internal.skyfall.htb
export VAULT_TOKEN=<TOKEN>
vault ssh --role dev_otp_key_role --mode otp --strict-host-key-checking=no askyy@skyfall.htb
```

## Movimiento lateral

`askyy` puede ejecutar `vault-unseal` como root. El binario escribe `debug.log` en el directorio actual con el token maestro; `askyy` no puede leerlo, pero sí controlar dónde se crea.

## Escalada de privilegios

Se monta un sistema FUSE `memfs` con `AllowOther`, se ejecuta `vault-unseal` dentro y se captura el contenido de `debug.log` en un archivo propiedad de `askyy`. El token maestro permite leer el rol SSH de root y entrar como root.

```bash
./memfs out/ out
cd out && sudo /root/vault/vault-unseal -c /etc/vault-unseal.yaml -vd
cat debug.log | grep 'Master token'
vault ssh --role admin_otp_key_role --mode otp root@skyfall.htb
```

## Evidencia

- MinIO con CVE-2023-28432 y credenciales root.
- Backup con `VAULT_TOKEN` y SSH OTP como `askyy`.
- `debug.log` capturado por FUSE y token maestro.

## Lecciones aprendidas

- Un servicio interno alcanzable por parsing inconsistente puede filtrar secretos.
- Los tokens de Vault deben tener el mínimo privilegio y no estar en dotfiles.
- FUSE puede capturar archivos que un proceso root escribe en un directorio controlado.

## Mitigación y detección

- Actualizar MinIO y aislar su API.
- Rotar tokens de Vault y limitar políticas SSH.
- Revisar montajes FUSE y binarios que escriban logs como root.

## Referencias

- [0xdf — Skyfall](https://0xdf.gitlab.io/2024/08/31/htb-skyfall.html)
- [IppSec — Skyfall](https://www.youtube.com/watch?v=jceaFKZUNYY)
- [Hack The Box — Skyfall](https://app.hackthebox.com/machines/skyfall)
