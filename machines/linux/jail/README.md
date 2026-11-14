---
machine: Jail
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, buffer-overflow, nfs, rvim, crypto]
---

# Jail — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El servicio 7411 es un binario de 32 bits con pila ejecutable y fuga de la dirección del buffer. Un overflow con shellcode reutiliza el socket y da shell como `nobody`. NFS con `no_all_squash` permite un SUID como `frank`; `rvim` escapa a `adm`, y un RAR cifrado más una clave RSA débil llevan a root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
22/tcp    ssh
80/tcp    http    Apache 2.4.6 (CentOS)
111/tcp   rpcbind
2049/tcp  nfs
7411/tcp  custom jail service
20048/tcp mountd
```

## Enumeración

- `showmount -e` lista `/opt` y `/var/nfsshare` exportados a cualquiera.
- `/opt` contiene el código fuente, el binario `jail` y `compile.sh`.
- El binario se compila con `-m32 -z execstack`, por lo que la pila es ejecutable.
- En modo `DEBUG` el servicio filtra la dirección del buffer `userpass`.

## Foothold

El protocolo pide `USER`, `PASS` y opcionalmente `DEBUG`. Con `DEBUG` se obtiene la dirección de `userpass`; el offset hasta EIP es 28 bytes. Se envía shellcode de reutilización de socket para conservar la conexión y se salta a la pila.

```text
USER admin
PASS  <28 bytes> + <addr+32> + <shellcode>
```

La shell resultante es `nobody`.

## Movimiento lateral

`/etc/exports` usa `root_squash` y `no_all_squash`. Un usuario local con UID 1000 se mapea a `frank` en el servidor. Se compila un binario que hace `setresuid(1000,1000,1000)` y ejecuta `/bin/bash`, se guarda en `/var/nfsshare` y se marca SUID.

Al ejecutarlo desde la shell de `nobody`, se obtiene `frank`.

```bash
gcc suid.c -o /mnt/nfsshare/suid
chmod 4777 /mnt/nfsshare/suid
```

## Escalada de privilegios

`frank` puede ejecutar `rvim` como `adm`. `rvim` restringe `:!`, pero permite `:python` o `:lua`; se usa para lanzar una shell y obtener `adm`.

En `/var/adm` hay una nota sobre la política de contraseñas, un fichero `.frank` en Atbash y `keys.rar`. El texto descifrado sugiere el nombre y el año de un fugitivo de Alcatraz; se genera una wordlist con reglas de `hashcat`, se crackea el RAR y se extrae una clave pública RSA.

La clave es débil y se factoriza con `RsaCtfTool`, que reconstruye la clave privada. Con ella se accede por SSH como root.

```bash
sudo -u adm /usr/bin/rvim /var/www/html/jailuser/dev/jail.c
hashcat --stdout -a 3 'Morris?d?d?d?d?s' > words.txt
rar2john keys.rar > keys.hash
john --wordlist=words.txt keys.hash
python3 RsaCtfTool.py --publickey rootauthorizedsshkey.pub --private
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales, si existen, viven en `private/` y no se publican.

## Lecciones aprendidas

- Un binario con pila ejecutable y fuga de dirección es un BOF directo.
- NFS con `no_all_squash` permite suplantar UIDs y crear SUID.
- `rvim` no es una jaula completa: `python` y `lua` escapan.
- Las contraseñas derivadas de datos públicos son predecibles.
- Una clave RSA corta o mal generada se factoriza.

## Mitigaciones y detección

- Compilar con NX, ASLR y sin filtraciones de direcciones.
- Exportar NFS con `all_squash` y `root_squash`, y restringir clientes.
- No permitir `rvim` con privilegios; usar un editor sin ejecución.
- Usar claves RSA de 2048 bits o más y passphrases robustas.

## Referencias

- [0xdf — Jail](https://0xdf.gitlab.io/2022/05/23/htb-jail.html)
- [Búsqueda de vídeos (CSV)](https://www.youtube.com/results?search_query=ippsec+jail+htb)
- [Búsqueda de writeups (CSV)](https://medium.com/search?q=hackthebox+jail+writeup)
